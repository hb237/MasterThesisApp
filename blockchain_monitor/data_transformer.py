from lxml.etree import SubElement
from datetime import datetime
from web3 import Web3


class DataTransformer():
    def add_time_stamps(self) -> None:
        # events = self.combined_xes.findall(".//event")
        for e in self.tranformed_xes.iter('event'):
            block_timestamp = int(
                e.find(".//int[@key='block_timestamp']").get('value'))
            date_time_value = datetime.utcfromtimestamp(
                block_timestamp).strftime('%Y-%m-%dT%H:%M:%SZ')

            data_time = SubElement(e, 'date')
            data_time.attrib['key'] = 'time:timestamp'
            data_time.attrib['value'] = date_time_value

    def add_cost(self) -> None:
        # traces = self.combined_xes.findall(".//trace")
        for t in self.tranformed_xes.iter('trace'):
            event_tx_elems = t.findall(".//event/string[@key='tx_hash']")
            event_txs = []
            for et in event_tx_elems:
                event_txs.append(et.get('value'))

            event_txs_counts = dict()
            for i in event_txs:
                event_txs_counts[i] = event_txs_counts.get(i, 0) + 1

            # events = t.findall(".//event")
            for e in t.iter('event'):
                currency = SubElement(e, 'string')
                currency.attrib['key'] = 'cost:currency'
                currency.attrib['value'] = 'ETH'

                gas_price = int(
                    e.find(".//int[@key='gas_price']").get('value'))
                gas_used = int(e.find(".//int[@key='gas_used']").get('value'))
                wei_cost = gas_price * gas_used
                ether_cost = Web3.fromWei(wei_cost, 'ether')
                cost = SubElement(e, 'float')
                cost.attrib['key'] = 'cost:total'
                cost.attrib['value'] = str(ether_cost)

                tx_hash = e.find(".//string[@key='tx_hash']").get('value')
                tx_number_of_events = SubElement(e, 'int')
                tx_number_of_events.attrib['key'] = 'tx_number_of_events'
                tx_number_of_events.attrib['value'] = str(event_txs_counts.get(
                    tx_hash))

    def transform_data(self, xes) -> None:
        self.tranformed_xes = xes
        self.add_time_stamps()
        self.add_cost()
        return self.tranformed_xes


# TODO remove, only for testing
if __name__ == '__main__':
    df = DataTransformer()
    df.transform_data()
