import lxml.etree as ET
from lxml.etree import Element, SubElement
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


class DataProcessor():
    def __init__(self) -> None:
        self.combined_xes: Element = None
        self.combined_xes = ET.parse(
            const.XES_FILES_COMBINED_PATH)  # TODO remove

    def add_time_stamps(self) -> None:
        events = self.combined_xes.findall(".//event")
        for e in events:
            block_timestamp = int(
                e.find(".//int[@key='block_timestamp']").get('value'))
            date_time_value = datetime.utcfromtimestamp(
                block_timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')

            data_time = SubElement(e, 'date')
            data_time.attrib['key'] = 'time:timestamp'
            data_time.attrib['value'] = date_time_value

    def add_cost(self) -> None:
        events = self.combined_xes.findall(".//event")
        for e in events:
            gas_price = int(e.find(".//int[@key='gas_price']").get('value'))
            gas_used = int(e.find(".//int[@key='gas_used']").get('value'))
            wei_cost = gas_price * gas_used
            ether_cost = Web3.fromWei(wei_cost, 'ether')

            data_time = SubElement(e, 'string')
            data_time.attrib['key'] = 'cost:currency'
            data_time.attrib['value'] = 'ETH'
            data_time = SubElement(e, 'string')
            data_time.attrib['key'] = 'cost:total'
            data_time.attrib['value'] = str(ether_cost)

    def save_combined_xes_to_file(self) -> None:
        with open(const.XES_FILES_COMBINED_PATH_TEST, 'wb') as f:  # TODO change path
            self.combined_xes.write(f)

    def transform_data(self) -> None:
        self.add_time_stamps()
        self.add_cost()
        self.save_combined_xes_to_file()


def read_log_filtered(from_block: int, to_block: int) -> EventLog:
    log = xes_importer.apply(
        const.XES_FILES_COMBINED_PATH_TEST)  # TODO change path
    filtered_log = attributes_filter.apply_numeric(log, from_block, to_block,
                                                   parameters={Parameters.CASE_ATTRIBUTE_PREFIX: '',
                                                               attributes_filter.Parameters.CASE_ID_KEY: 'ident:piid',
                                                               attributes_filter.Parameters.ATTRIBUTE_KEY: 'tx_blocknumber',
                                                               attributes_filter.Parameters.POSITIVE: True})
    return filtered_log


def get_petri_net(from_block: int, to_block: int) -> str:
    log = read_log_filtered(from_block, to_block)
    net, initial_marking, final_marking = inductive_miner.apply(log)
    path = "static/diagrams/pteri_net_" + \
        str(from_block) + "-" + str(to_block) + ".png"
    pm4py.save_vis_petri_net(net, initial_marking,
                             final_marking, path)  # TODO use constant
    return path
    # pm4py.view_petri_net(net, initial_marking, final_marking, format='png')
    # TODO remove visualization and save png


def get_bmpn_diagram(from_block: int, to_block: int, noise_threshold: float = 0.8) -> str:
    log = read_log_filtered(from_block, to_block)
    bpmn_graph = pm4py.discover_bpmn_inductive(log, noise_threshold)
    path = "static/diagrams/bpmn_diagram" + \
        str(from_block) + "-" + str(to_block) + ".png"
    pm4py.save_vis_bpmn(bpmn_graph, path)
    return path


def get_dfg_frequency(from_block: int, to_block: int):
    log = read_log_filtered(from_block, to_block)
    dfg = dfg_discovery.apply(log, variant=dfg_discovery.Variants.FREQUENCY)
    # TODO remove visualization and save png
    gviz = dfg_visualization.apply(
        dfg, log=log, variant=dfg_visualization.Variants.FREQUENCY)
    dfg_visualization.view(gviz)


def get_dfg_performance(from_block: int, to_block: int):
    log = read_log_filtered(from_block, to_block)
    # annotate with gas costs?
    dfg = dfg_discovery.apply(log, variant=dfg_discovery.Variants.PERFORMANCE)
    # TODO remove visualization and save png
    gviz = dfg_visualization.apply(
        dfg, log=log, variant=dfg_visualization.Variants.PERFORMANCE)
    dfg_visualization.view(gviz)


def get_last_events(number_events):
    xes_log = ET.parse(const.XES_FILES_COMBINED_PATH_TEST)
    events = xes_log.findall(".//event")
    events = sorted(events, key=lambda e: int(
        e.find(".//int[@key='tx_blocknumber']").get('value')), reverse=True)
    return events[:number_events]


def get_events(from_block: int, to_block: int):
    xes_log = ET.parse(const.XES_FILES_COMBINED_PATH_TEST)
    events = xes_log.findall(".//event")
    events = filter(lambda e: from_block <= int(
        e.find(".//int[@key='tx_blocknumber']").get('value')) <= to_block, events)
    events = sorted(events, key=lambda e: int(
        e.find(".//int[@key='tx_blocknumber']").get('value')), reverse=True)
    return events


def get_eth_rates():
    'Retrieves the current currency rates fro a multitude of currencies to pay for 1 ETH.'
    res = requests.get(
        'https://api.coinbase.com/v2/exchange-rates?currency=ETH')
    return res.json()['data']['rates']


def get_current_block_stats() -> dict:
    # TODO launch geth client with:
    # set --datadir appropriately
    # geth --syncmode "light" --ws --ws.addr 127.0.0.1 --ws.port 8546 --datadir="/media/hendrik/SSD-1TB/geth"
    w3 = Web3(Web3.WebsocketProvider('ws://127.0.0.1:8546'))
    current_block_number = int(w3.eth.get_block_number())
    current_block_timestamp = datetime.utcfromtimestamp(int(w3.eth.getBlock(
        current_block_number).timestamp)).strftime('%Y-%m-%d %H:%M:%S UTC+0')
    return {'current_block_number': current_block_number, 'current_block_timestamp': current_block_timestamp}


def get_block_stats() -> dict:
    '''Returns a dictionary with all blocks as key and how many events happend in that block.'''
    log = xes_importer.apply(const.XES_FILES_COMBINED_PATH_TEST)
    block_stats = attributes_filter.get_attribute_values(log, "tx_blocknumber")
    return block_stats


def get_sender_stats(from_block: int, to_block: int):
    log = read_log_filtered(from_block, to_block)
    sender_stats = attributes_filter.get_attribute_values(log, "tx_from")
    return sender_stats


def get_receiver_stats(from_block: int, to_block: int):
    log = read_log_filtered(from_block, to_block)
    receiver_stats = attributes_filter.get_attribute_values(log, "tx_to")
    return receiver_stats


def conformance_checking(from_block: int, to_block: int):
    log = read_log_filtered(from_block, to_block)
    bpmn_graph = get_bmpn_diagram(6605100, 6606100, 1)  # TODO remove
    # bpmn_graph = pm4py.read_bpmn("path_to_bpmn") #TODO change path and check if path location not empty
    net, initial_marking, final_marking = bpmn_converter.apply(bpmn_graph)
    replayed_traces = token_replay.apply(
        log, net, initial_marking, final_marking)
    return replayed_traces


def save_bpmn_model(bpmn_model):
    # bpmn modul MUST ONLY contain
    # Events (start / end events)
    # Tasks
    # Gateways (exclusive, parallel, inclusive)
    return


def set_manifest_file(mainfest):
    return


def validate_current_manifest():
    return


def launch_file_reader():
    return


def set_input_src(type, speed):
    # type : feeder, blf
    # speed of file feeder
    # either file feeder or blf
    return


def launch_file_feeder():
    return


def launch_blf():
    return


def reset_application():
    # delete all gathered data
    return


if __name__ == '__main__':
    dp = DataProcessor()
    dp.transform_data()
    print(conformance_checking(6605100, 6606100))
