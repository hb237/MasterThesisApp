import lxml.etree as ET
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.conformance.tokenreplay import algorithm as token_based_replay
from pm4py.visualization.dfg import visualizer as dfg_visualization
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.conversion.log.variants.to_event_log import Parameters
from pm4py.objects.conversion.bpmn import converter as bpmn_converter
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
from multiprocessing import Process
from datetime import datetime
from collections import Counter
import constants as const
import blockchain_connector as bc
import requests
import bpmn_with_costs
import json
import time
import app
import os
import shutil
from test_app import file_feeder
from file_merger import FileMerger
import time


STREAM_LIVE = 'streaming-live-data'
STREAM_EXAMPLE = 'streaming-example-data'
STATIC = 'static-example-data'


class DataProcessor():
    def __init__(self) -> None:
        self.analysis_process: Process = None
        self.file_feeder_process: Process = None
        self.file_merger_process: Process = None

    def check_monitoring_running(self) -> bool:
        if self.analysis_process is not None:
            return self.analysis_process.is_alive()

    def set_settings(self):
        with open(const.SETTINGS_PATH) as json_file:
            config = json.loads(json_file.read())

        self.last_x_blocks: bool = json.loads(
            config.get('chkLastXBlocks', 'false'))
        self.recent_block: bool = json.loads(
            config.get('chkRecentBlock', 'false'))
        self.confirmation_blocks = int(config.get(
            'inputConfirmationBlocks', 0))
        self.end_block = int(config.get(
            'inputEndBlock', 0))
        self.start_block = int(config.get(
            'inputStartBlock', 0))
        self.refresh_rate = int(config.get(
            'inputRefreshRate', 1))
        self.replay_speed = int(config.get(
            'inputReplaySpeed', 1))
        self.noise_threshold = float(config.get(
            'inputNoiseThreshold', 0.8))
        self.currency = self.geth_ip = str(
            config.get('selectCurrency', 'EUR'))
        self.data_set = str(
            config.get('selectDataSet', ''))
        self.input_mode = str(
            config.get('selectInputMode', STREAM_EXAMPLE))

    def stop_processing(self):
        if self.file_feeder_process is not None:
            self.file_feeder_process.join(timeout=0)
            self.file_feeder_process.terminate()
        if self.file_merger_process is not None:
            self.file_merger_process.join(timeout=0)
            self.file_merger_process.terminate()
        if self.analysis_process is not None:
            self.analysis_process.join(timeout=0)
            self.analysis_process.terminate()
        # delete all xes files in input folder
        shutil.rmtree(const.XES_FILES_DIR)
        if not os.path.exists(const.XES_FILES_DIR):
            os.makedirs(const.XES_FILES_DIR)

    def start_processing(self):
        self.set_settings()

        self.stop_processing()

        # TODO
        # Fixed range: start = static and end = static
        # Floating range: start = current and end = current - x blocks
        # Growing range: start = current and end = static
        fm = FileMerger()
        self.file_merger_process = Process(
            target=fm.merge
        )
        self.file_merger_process.start()

        if self.input_mode == STATIC:
            self.analysis_process = Process(
                target=self.process_data,
            )
            self.analysis_process.start()
        elif self.input_mode == STREAM_EXAMPLE:
            self.file_feeder_process = Process(
                target=file_feeder.feed_files
            )
            self.file_feeder_process.start()
        elif self.input_mode == STREAM_LIVE:
            app.extract_current_manifest()
        if self.input_mode == STREAM_EXAMPLE or self.input_mode == STREAM_LIVE:
            self.analysis_process = Process(
                target=self.continuously_process_data,
            )
            self.analysis_process.start()

    def continuously_process_data(self):
        while(True):
            self.process_data()

    def process_data(self):
        if not os.path.exists(const.XES_FILES_COMBINED_PATH):
            time.sleep(1)
            return

        self.retreive_current_block_stats()
        self.create_shared_datastructures()

        # Execute all analysis methods
        self.retreive_eth_rates()
        self.create_petri_net()
        self.create_bmpn_diagram(noise_threshold=0.8)
        self.create_bpmn_diagram_with_costs(
            currency='EUR', currency_rate=1.0, noise_threshold=0.8)
        self.create_dfg_frequency()
        self.create_dfg_performance()
        self.retreive_traces()
        self.retreive_events()
        self.retreive_block_stats()
        self.retreive_sender_stats()
        self.retreive_receiver_stats()
        self.execute_conformance_checking()
        self.write_last_time_updated()

    def create_shared_datastructures(self):
        # Create a pm4py log as on input for further analysis
        log = xes_importer.apply(
            const.XES_FILES_COMBINED_PATH)
        self.pm4py_log = attributes_filter.apply_numeric(log, self.start_block, self.end_block,
                                                         parameters={Parameters.CASE_ATTRIBUTE_PREFIX: '',
                                                                     attributes_filter.Parameters.CASE_ID_KEY: 'ident:piid',
                                                                     attributes_filter.Parameters.ATTRIBUTE_KEY: 'tx_blocknumber',
                                                                     attributes_filter.Parameters.POSITIVE: True})
        # Read in log as tree
        self.xes_log_tree = ET.parse(const.XES_FILES_COMBINED_PATH)

    def write_last_time_updated(self):
        t = time.time()
        date_time_value = datetime.utcfromtimestamp(
            t).strftime('%Y-%m-%d %H:%M:%S UTC+0')
        with open(const.DATASET_LAST_UPDATE, "w") as file:
            json.dump(date_time_value, file)

    def create_petri_net(self):
        net, im, fm = inductive_miner.apply(
            self.pm4py_log)
        pm4py.save_vis_petri_net(
            net, im, fm, const.PETRI_NET)

    def create_bmpn_diagram(self, noise_threshold: float = 0.8):
        bpmn_graph = pm4py.discover_bpmn_inductive(
            self.pm4py_log, noise_threshold)
        pm4py.save_vis_bpmn(bpmn_graph, const.BPMN_DIAGRAM)

    def create_bpmn_diagram_with_costs(self, currency: str, currency_rate: float, noise_threshold: float = 0.8):
        bpmn_graph = pm4py.discover_bpmn_inductive(
            self.pm4py_log, noise_threshold)
        gviz = bpmn_with_costs.apply(
            bpmn_graph, self.xes_log_tree, currency, currency_rate=3000, ndigits=2, format='png')  # TODO
        bpmn_visualizer.save(gviz, const.BPMN_COSTS_DIAGRAM)

    def create_dfg_frequency(self):
        dfg = dfg_discovery.apply(
            self.pm4py_log, variant=dfg_discovery.Variants.FREQUENCY)
        parameters = {
            dfg_visualization.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
        gviz = dfg_visualization.apply(
            dfg, log=self.pm4py_log, variant=dfg_visualization.Variants.FREQUENCY, parameters=parameters)
        dfg_visualization.save(gviz, const.DFG_FREQUENCY)

    def create_dfg_performance(self) -> str:
        dfg = dfg_discovery.apply(
            self.pm4py_log, variant=dfg_discovery.Variants.PERFORMANCE)
        parameters = {
            dfg_visualization.Variants.PERFORMANCE.value.Parameters.FORMAT: "png"}
        gviz = dfg_visualization.apply(
            dfg, log=self.pm4py_log, variant=dfg_visualization.Variants.PERFORMANCE, parameters=parameters)
        dfg_visualization.save(gviz, const.DFG_PERFORMANCE)

    def retreive_traces(self):
        traces = self.xes_log_tree.findall(".//trace")  # TODO
        # with open(const.TRACES, "w") as file:
        #     json.dump(traces, file, indent=4, sort_keys=True)

    def retreive_events(self):
        events = self.xes_log_tree.findall(".//event")
        events = filter(lambda e: self.start_block <= int(
            e.find(".//int[@key='tx_blocknumber']").get('value')) <= self.end_block, events)
        events = sorted(events, key=lambda e: int(
            e.find(".//int[@key='tx_blocknumber']").get('value')), reverse=True)
        # with open(const.EVENTS, "w") as file: #TODO
        #     json.dump(events, file, indent=4, sort_keys=True)

    def retreive_eth_rates(self):
        'Retrieves the current currency rates fro a multitude of currencies to pay for 1 ETH.'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', }
        res = requests.get(
            'https://api.coinbase.com/v2/exchange-rates?currency=ETH', headers=headers, timeout=1)
        rates = res.json()['data']['rates']
        for rate in rates:
            rates[rate] = float(rates[rate])
        self.rates = rates
        with open(const.ETH_RATES, "w") as file:
            json.dump(rates, file)

    def retreive_current_block_stats(self):
        # Get current block number and its timestamp
        stats = bc.get_current_block_stats()
        if stats is not None:
            self.current_block_number = stats.get('current_block_number', 0)
            self.current_block_timestamp = stats.get(
                'current_block_timestamp', 0)
        with open(const.CURRENT_BLOCK_STATS, "w") as file:
            json.dump(stats, file)

    def retreive_block_stats(self):
        '''Returns a dictionary with all blocks as key and how many events happend in that block.'''
        stats = attributes_filter.get_attribute_values(
            self.pm4py_log, "tx_blocknumber")
        result = []
        for block, cnt in stats.items():
            result.append({'Block': block, 'Number of Events': cnt})
        with open(const.BLOCK_STATS, "w") as file:
            json.dump(result, file)

    def retreive_sender_stats(self):
        stats = attributes_filter.get_attribute_values(
            self.pm4py_log, "tx_from")
        result = []
        for sender, cnt in stats.items():
            result.append({'Sender': sender, 'Number of Events': str(cnt)})
        with open(const.SENDER_STATS, "w") as file:
            json.dump(result, file)

    def retreive_receiver_stats(self):
        stats = attributes_filter.get_attribute_values(
            self.pm4py_log, "tx_to")
        result = []
        for receiver, cnt in stats.items():
            result.append({'Receiver': receiver, 'Number of Events': str(cnt)})
        self.receiver_stats = result
        with open(const.RECEIVER_STATS, "w") as file:
            json.dump(result, file)

    def execute_conformance_checking(self):
        bpmn_graph = pm4py.read_bpmn(const.BPMN_PATH)
        net, initial_marking, final_marking = bpmn_converter.apply(bpmn_graph)

        parameters_tbr = {token_based_replay.Variants.TOKEN_REPLAY.value.Parameters.DISABLE_VARIANTS: True,
                          token_based_replay.Variants.TOKEN_REPLAY.value.Parameters.ENABLE_PLTR_FITNESS: True}
        replayed_traces, place_fitness, trans_fitness, unwanted_activities = \
            token_based_replay.apply(
                self.pm4py_log, net, initial_marking, final_marking, parameters=parameters_tbr)

        # activities that are recorded in the log but not in the model
        # count how often they occur
        unwanted_activities_stats = []
        for activity in unwanted_activities.keys():
            unwanted_activities_stats.append({'Activity': activity, 'Count in log': str(len(
                unwanted_activities[activity]))})
        with open(const.CC_UNWANTED_ACTIVITIES_STATS, "w") as file:
            json.dump(unwanted_activities_stats, file)

        # activities that are in model but not in the log
        activities_stats = []
        for activity in trans_fitness.keys():
            not_in_model = len(trans_fitness[activity]['underfed_traces']) == 0 and len(
                trans_fitness[activity]['fit_traces']) == 0
            activities_stats.append(
                {'activity': str(activity), 'not_in_model': not_in_model})
        with open(const.CC_ACTIVITIES_STATS, "w") as file:
            json.dump(activities_stats, file)

        # the different fitness values and how often each occurred
        trace_fitness_stats = []
        trace_fitnesses = []
        for t in replayed_traces:
            trace_fitnesses.append(t['trace_fitness'])
        counted = dict(Counter(trace_fitnesses))
        for k in counted.keys():
            trace_fitness_stats.append({'fitness': k, 'count': counted[k]})
        with open(const.CC_TRACE_FITNESS_STATS, "w") as file:
            json.dump(trace_fitness_stats, file)
