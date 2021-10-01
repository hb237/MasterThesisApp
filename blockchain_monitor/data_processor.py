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


STREAM_LIVE = 'streaming-live-data'
STREAM_EXAMPLE = 'streaming-example-data'
STATIC = 'static'


class DataProcessor():
    def __init__(self) -> None:
        self.analysis_process: Process = None

    def check_monitoring_running(self) -> bool:
        if self.analysis_process is None:
            return False
        else:
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
        if self.analysis_process is not None:
            self.analysis_process.join(timeout=1)
            self.analysis_process.terminate()

    def init_processing(self):
        self.set_settings()

        # Terminate running process
        if self.analysis_process is not None:
            self.analysis_process.terminate()

        # Fixed range: start = static and end = static
        # Floating range: start = current and end = current - x blocks
        # Growing range: start = current and end = static

        if self.input_mode == STATIC:
            self.process_data()
        elif self.input_mode == STREAM_EXAMPLE:
            # TODO launch file feeder
            # TODO get selected example files
            pass
        elif self.input_mode == STREAM_LIVE:
            # TODO launch BLF
            pass

        if self.input_mode == STREAM_EXAMPLE or self.input_mode == STREAM_LIVE:
            self.analysis_process = Process(
                target=self.continuously_process_data,
                daemon=True
            )
            self.analysis_process.start()

    def continuously_process_data(self):
        pass
        # while(True):
        #     self.process_data()

    def process_data(self):
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
        self.retreive_current_block_stats()

        # Create a pm4py log as on input for further analysis
        log = xes_importer.apply(
            const.XES_FILES_COMBINED_PATH_TEST)  # TODO change path
        self.pm4py_log = attributes_filter.apply_numeric(log, self.start_block, self.end_block,
                                                         parameters={Parameters.CASE_ATTRIBUTE_PREFIX: '',
                                                                     attributes_filter.Parameters.CASE_ID_KEY: 'ident:piid',
                                                                     attributes_filter.Parameters.ATTRIBUTE_KEY: 'tx_blocknumber',
                                                                     attributes_filter.Parameters.POSITIVE: True})
        # Read in log as tree
        self.xes_log_tree = ET.parse(const.XES_FILES_COMBINED_PATH_TEST)

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
            bpmn_graph, self.xes_log_tree, currency, currency_rate, ndigits=2, format='png')
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
        # replayed_traces: group py fitness in deciles and show bar chart how many traces per decile
        # trans_fitness: take tasks with {'underfed_traces': {}, 'fit_traces': {}} meaning they are in the model but not in the log -> list them
        # unwanted_activities: list all task and how many events with this missing task

        unwanted_activities_stats = {}
        for activity in unwanted_activities.keys():
            unwanted_activities_stats[activity] = len(
                unwanted_activities[activity])
        print(unwanted_activities_stats)

        activities_stats = {}
        for activity in trans_fitness.keys():
            not_in_model = len(trans_fitness[activity]['underfed_traces']) == 0 and len(
                trans_fitness[activity]['fit_traces']) == 0
            activities_stats[activity] = not_in_model
        print(activities_stats)

        traces_stats = {}
        trace_fitnesses = []
        for t in replayed_traces:
            trace_fitnesses.append(t['trace_fitness'])
        traces_stats = dict(Counter(trace_fitnesses))
        print(traces_stats)

        # with open(const.CONFORMANCE_CHECKING_RESULTS, "w") as file:
        #     json.dump(result, file)
        return
