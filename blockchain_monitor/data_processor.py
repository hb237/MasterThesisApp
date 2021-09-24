import lxml.etree as ET
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.conformance.tokenreplay import algorithm as token_replay
from pm4py.objects.log.obj import EventLog
from pm4py.visualization.dfg import visualizer as dfg_visualization
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.conversion.log.variants.to_event_log import Parameters
from pm4py.objects.conversion.bpmn import converter as bpmn_converter
import constants as const
from datetime import datetime
from web3 import Web3
import requests


def read_log_filtered(from_block: int, to_block: int) -> EventLog:
    log = xes_importer.apply(
        const.XES_FILES_COMBINED_PATH_TEST)  # TODO change path
    filtered_log = attributes_filter.apply_numeric(log, from_block, to_block,
                                                   parameters={Parameters.CASE_ATTRIBUTE_PREFIX: '',
                                                               attributes_filter.Parameters.CASE_ID_KEY: 'ident:piid',
                                                               attributes_filter.Parameters.ATTRIBUTE_KEY: 'tx_blocknumber',
                                                               attributes_filter.Parameters.POSITIVE: True})
    return filtered_log


class DataProcessor():
    def __init__(self, from_block: int, to_block: int) -> None:
        self.log = read_log_filtered(from_block, to_block)
        self.from_block = from_block
        self.to_block = to_block

    def get_petri_net(self) -> str:
        net, initial_marking, final_marking = inductive_miner.apply(self.log)
        path = "static/diagrams/pteri_net_" + \
            str(self.from_block) + "-" + str(self.to_block) + ".png"
        pm4py.save_vis_petri_net(net, initial_marking,
                                 final_marking, path)  # TODO use constant
        return path

    def get_bmpn_diagram(self, noise_threshold: float = 0.8) -> str:
        bpmn_graph = pm4py.discover_bpmn_inductive(self.log, noise_threshold)
        path = "static/diagrams/bpmn_diagram" + \
            str(self.from_block) + "-" + str(self.to_block) + ".png"
        pm4py.save_vis_bpmn(bpmn_graph, path)
        return path

    def get_dfg_frequency(self):
        dfg = dfg_discovery.apply(
            self.log, variant=dfg_discovery.Variants.FREQUENCY)
        # TODO remove visualization and save png
        gviz = dfg_visualization.apply(
            dfg, log=self.log, variant=dfg_visualization.Variants.FREQUENCY)
        dfg_visualization.view(gviz)

    def get_dfg_performance(self):
        # annotate with gas costs?
        dfg = dfg_discovery.apply(
            self.log, variant=dfg_discovery.Variants.PERFORMANCE)
        # TODO remove visualization and save png
        gviz = dfg_visualization.apply(
            dfg, log=self.log, variant=dfg_visualization.Variants.PERFORMANCE)
        dfg_visualization.view(gviz)

    def get_last_events(self, number_events):
        xes_log = ET.parse(const.XES_FILES_COMBINED_PATH_TEST)
        events = xes_log.findall(".//event")
        events = sorted(events, key=lambda e: int(
            e.find(".//int[@key='tx_blocknumber']").get('value')), reverse=True)
        return events[:number_events]

    def get_events(self):
        xes_log = ET.parse(const.XES_FILES_COMBINED_PATH_TEST)
        events = xes_log.findall(".//event")
        events = filter(lambda e: self.from_block <= int(
            e.find(".//int[@key='tx_blocknumber']").get('value')) <= self.to_block, events)
        events = sorted(events, key=lambda e: int(
            e.find(".//int[@key='tx_blocknumber']").get('value')), reverse=True)
        return events

    def get_eth_rates(self):
        'Retrieves the current currency rates fro a multitude of currencies to pay for 1 ETH.'
        res = requests.get(
            'https://api.coinbase.com/v2/exchange-rates?currency=ETH')
        return res.json()['data']['rates']

    def get_current_block_stats(self) -> dict:
        # TODO launch geth client with:
        # set --datadir appropriately
        # geth --syncmode "light" --ws --ws.addr 127.0.0.1 --ws.port 8546 --datadir="/media/hendrik/SSD-1TB/geth"
        w3 = Web3(Web3.WebsocketProvider('ws://127.0.0.1:8546'))
        current_block_number = int(w3.eth.get_block_number())
        current_block_timestamp = datetime.utcfromtimestamp(int(w3.eth.getBlock(
            current_block_number).timestamp)).strftime('%Y-%m-%d %H:%M:%S UTC+0')
        return {'current_block_number': current_block_number, 'current_block_timestamp': current_block_timestamp}

    def get_block_stats(self) -> dict:
        '''Returns a dictionary with all blocks as key and how many events happend in that block.'''
        return attributes_filter.get_attribute_values(
            self.log, "tx_blocknumber")

    def get_sender_stats(self):
        return attributes_filter.get_attribute_values(
            self.log, "tx_from")

    def get_receiver_stats(self):
        return attributes_filter.get_attribute_values(
            self.log, "tx_to")

    def conformance_checking(self):
        bpmn_graph = self.get_bmpn_diagram(6605100, 6606100, 1)  # TODO remove
        # bpmn_graph = pm4py.read_bpmn("path_to_bpmn") #TODO change path and check if path location not empty
        net, initial_marking, final_marking = bpmn_converter.apply(bpmn_graph)
        replayed_traces = token_replay.apply(
            self.log, net, initial_marking, final_marking)
        return replayed_traces
