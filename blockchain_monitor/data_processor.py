import lxml.etree as ET
from lxml.etree import Element, SubElement, ElementTree
import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualization
import constants as const
from datetime import datetime
from web3 import Web3
class DataProcessor():
    def __init__(self) -> None:
        self.combined_xes: Element = None
        self.combined_xes =  ET.parse(const.XES_FILES_COMBINED_PATH) # TODO remove

    def add_time_stamps(self):
        events = self.combined_xes.findall(".//event")
        for e in events:
            block_timestamp = int(e.find(".//int[@key='block_timestamp']").get('value'))
            date_time_value = datetime.utcfromtimestamp(block_timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            data_time = SubElement(e, 'date')
            data_time.attrib['key'] = 'time:timestamp'
            data_time.attrib['value'] = date_time_value

    def add_cost(self):
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

    def save_combined_xes_to_file(self):
        with open(const.XES_FILES_COMBINED_PATH_TEST, 'wb') as f:
            # tree = ElementTree(self.combined_xes)
            # tree.write(f)
            self.combined_xes.write(f)

    def transform_data(self):
        self.add_time_stamps()
        self.add_cost()
        self.save_combined_xes_to_file()

def analyse_xes_file():
    # TODO write combined_xes to file # could be async

    # display petri net
    log = xes_importer.apply(const.XES_FILES_COMBINED_PATH_TEST)
    net, initial_marking, final_marking = inductive_miner.apply(log)
    pm4py.view_petri_net(net, initial_marking, final_marking, format='png') 

    # displaying event and transition frequency
    dfg = dfg_discovery.apply(log, variant=dfg_discovery.Variants.FREQUENCY)
    gviz = dfg_visualization.apply(dfg, log=log, variant=dfg_visualization.Variants.FREQUENCY)
    dfg_visualization.view(gviz)

    # displaying time for event and transitions in between them
    dfg = dfg_discovery.apply(log, variant=dfg_discovery.Variants.PERFORMANCE)
    gviz = dfg_visualization.apply(dfg, log=log, variant=dfg_visualization.Variants.PERFORMANCE)
    dfg_visualization.view(gviz)


if __name__ == '__main__':
    dp = DataProcessor()
    dp.transform_data()
    analyse_xes_file()