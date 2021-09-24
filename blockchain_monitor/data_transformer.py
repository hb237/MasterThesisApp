import lxml.etree as ET
from lxml.etree import Element, SubElement
import constants as const
from datetime import datetime
from web3 import Web3


class DataTransformer():
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
