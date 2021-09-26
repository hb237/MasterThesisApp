from sys import gettrace
from typing import List
import lxml.etree as ET
from lxml.etree import Element
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
import requests
import bpmn_with_costs
from pm4py.visualization.bpmn import visualizer as bpmn_visualizer
import json


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
        # TODO trigger only if needed
        self.pm4py_log = read_log_filtered(from_block, to_block)
        # TODO trigger only if needed
        self.xes_log_tree = ET.parse(const.XES_FILES_COMBINED_PATH_TEST)
        self.from_block = from_block
        self.to_block = to_block

    def get_petri_net(self) -> str:
        net, initial_marking, final_marking = inductive_miner.apply(
            self.pm4py_log)
        path = const.DIAGRAMS_PATH + "pteri_net_" + \
            str(self.from_block) + "-" + str(self.to_block) + ".png"
        pm4py.save_vis_petri_net(net, initial_marking, final_marking, path)
        return path

    def get_bmpn_diagram(self, noise_threshold: float = 0.8) -> str:
        bpmn_graph = pm4py.discover_bpmn_inductive(
            self.pm4py_log, noise_threshold)
        path = const.DIAGRAMS_PATH + "bpmn_diagram" + \
            str(self.from_block) + "-" + str(self.to_block) + ".png"
        pm4py.save_vis_bpmn(bpmn_graph, path)
        return path

    # TODO reuse bpmn graph
    # TODO reuse get_events result
    # TODO reuse get eth rates
    def get_bpmn_diagram_with_costs(self, currency: str, currency_rate: float, noise_threshold: float = 0.8) -> str:
        bpmn_graph = pm4py.discover_bpmn_inductive(
            self.pm4py_log, noise_threshold)
        path = const.DIAGRAMS_PATH + "bpmn_diagram_with_costs" + \
            str(self.from_block) + "-" + str(self.to_block) + ".png"
        format = path[path.index(".") + 1:].lower()
        gviz = bpmn_with_costs.apply(
            bpmn_graph, self.xes_log_tree, currency, currency_rate, ndigits=2, format=format)
        bpmn_visualizer.save(gviz, path)
        return path

    # TODO enable filtering
    def get_dfg_frequency(self) -> str:
        dfg = dfg_discovery.apply(
            self.pm4py_log, variant=dfg_discovery.Variants.FREQUENCY)
        parameters = {
            dfg_visualization.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
        gviz = dfg_visualization.apply(
            dfg, log=self.pm4py_log, variant=dfg_visualization.Variants.FREQUENCY, parameters=parameters)
        path = const.DIAGRAMS_PATH + "dfg_diagramm_frequency" + \
            str(self.from_block) + "-" + str(self.to_block) + ".png"
        dfg_visualization.save(gviz, path)
        return path

    # TODO enable filtering
    def get_dfg_performance(self) -> str:
        dfg = dfg_discovery.apply(
            self.pm4py_log, variant=dfg_discovery.Variants.PERFORMANCE)
        parameters = {
            dfg_visualization.Variants.PERFORMANCE.value.Parameters.FORMAT: "png"}
        gviz = dfg_visualization.apply(
            dfg, log=self.pm4py_log, variant=dfg_visualization.Variants.PERFORMANCE, parameters=parameters)
        path = const.DIAGRAMS_PATH + "dfg_diagramm_performance" + \
            str(self.from_block) + "-" + str(self.to_block) + ".png"
        dfg_visualization.save(gviz, path)
        return path

    def get_traces(self) -> List[Element]:
        return self.xes_log_tree.findall(".//trace")

    def get_events(self) -> List[Element]:
        events = self.xes_log_tree.findall(".//event")
        events = filter(lambda e: self.from_block <= int(
            e.find(".//int[@key='tx_blocknumber']").get('value')) <= self.to_block, events)
        events = sorted(events, key=lambda e: int(
            e.find(".//int[@key='tx_blocknumber']").get('value')), reverse=True)
        return events

    def get_eth_rates(self) -> dict:
        'Retrieves the current currency rates fro a multitude of currencies to pay for 1 ETH.'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36', }
        res = requests.get(
            'https://api.coinbase.com/v2/exchange-rates?currency=ETH', headers=headers, timeout=1)
        rates = res.json()['data']['rates']
        for rate in rates:
            rates[rate] = float(rates[rate])
        return rates

    def get_attribute_stats(self, attribute_name: str) -> dict:
        return attributes_filter.get_attribute_values(self.pm4py_log, attribute_name)

    # TODO remove and use get_attribute_stats
    def get_block_stats(self) -> dict:
        '''Returns a dictionary with all blocks as key and how many events happend in that block.'''
        return attributes_filter.get_attribute_values(
            self.pm4py_log, "tx_blocknumber")

    # TODO remove and use get_attribute_stats
    def get_sender_stats(self) -> dict:
        sender_stats = attributes_filter.get_attribute_values(
            self.pm4py_log, "tx_from")
        result = []
        for sender, cnt in sender_stats.items():
            result.append({'Sender': sender, 'Number of Events': str(cnt)})
        return json.dumps(result)

    # TODO remove and use get_attribute_stats
    def get_receiver_stats(self) -> dict:
        return attributes_filter.get_attribute_values(
            self.pm4py_log, "tx_to")

    def conformance_checking(self):  # TODO not done yet
        bpmn_graph = self.get_bmpn_diagram(6605100, 6606100, 1)  # TODO remove
        # bpmn_graph = pm4py.read_bpmn("path_to_bpmn") #TODO change path and check if path location not empty
        net, initial_marking, final_marking = bpmn_converter.apply(bpmn_graph)
        replayed_traces = token_replay.apply(
            self.pm4py_log, net, initial_marking, final_marking)
        return replayed_traces
