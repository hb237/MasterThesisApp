# Keep in mind that lxml supports only xPath 1.0
#from web3 import Web3
#w3 = Web3(Web3.WebsocketProvider('wss://mainnet.infura.io/ws/v3/bcf5331eacae4b0c8fba1751b28c6768'))
import os
import time
import lxml.etree as ET
from lxml.etree import Element
from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from data_transformer import DataTransformer
import constants as const


class FileMerger():
    def __init__(self) -> None:
        # TODO set parameters
        self.combined_xes = None
        self.last_blk = None
        self.first_blk = None
        self.max_block_range = 10000

    def add_traces(self, path: str):
        # read in new xes file as tree
        tree = None
        attempts = 0
        # Sometimes the file is not fully created yet.
        # However, the parser already tries to read the empty file.
        # A few milliseconds later the file should not be empty anymore.
        while tree is None and attempts < 5:
            try:
                tree = ET.parse(path)
                attempts += 1
            except ET.XMLSyntaxError:
                time.sleep(0.1)

        if tree is None:
            raise Exception('Could not parse file: ' + path)

        # retreive all new trace from the xes file's tree
        root = tree.getroot()

        current_block_number = int(root.find(
            ".//int[@key='tx_blocknumber']").get('value'))

        self.first_blk = current_block_number
        if(self.last_blk is not None):
            block_range = self.first_blk - self.last_blk
            if block_range >= self.max_block_range:
                self.last_blk = self.first_blk - self.max_block_range
                self.remove_old_events(self.last_blk)
        else:
            self.last_blk = self.first_blk

        for new_trace in root.iter('trace'):
            new_trace_piid = new_trace.find(
                ".//string[@key='ident:piid']").get('value')
            existing_piids = self.combined_xes.findall(
                ".//string[@key='ident:piid']")

            # find if a trace with the new process instance id exists
            # only one or none should exist
            trace = None
            for ep in existing_piids:
                if(ep.get('value') == new_trace_piid):
                    trace = ep.find("..")
                    break

            dt = DataTransformer()
            new_trace = dt.transform_data(new_trace)

            # append the trace if it does not exist yet
            if(trace == None):
                self.combined_xes.append(new_trace)
            # add all new events to the existing trace
            else:
                new_events = new_trace.findall(".//event")
                for event in new_events:
                    trace.append(event)

        with open(const.XES_FILES_COMBINED_PATH_TEST, 'wb') as f:  # TODO change path
            print('Combined XES was extended by: ' + path)
            f.write(ET.tostring(self.combined_xes, pretty_print=True))

    def remove_old_events(self, block_nr: int):
        for event in self.combined_xes.iter('event'):
            if int(event.find(".//int[@key='tx_blocknumber']").get('value')) <= block_nr:
                event.getparent().remove(event)
        for trace in self.combined_xes.iter('trace'):
            if(trace.find(".//event") is None):
                trace.getparent().remove(trace)

    class InputHandler(FileSystemEventHandler):
        def __init__(self) -> None:
            super().__init__()

        # Once BLF extracted a XES file from a new block write its trace to the combined log.
        def on_created(self, event):
            if type(event) == FileCreatedEvent:
                self.add_traces(event.src_path, self.dp)  # TODO

    def start(self):
        print('Started file reader.')

        # setup xes log structure
        self.combined_xes = Element('log')
        self.combined_xes.attrib['xes.version'] = '1.0'
        self.combined_xes.attrib['xes.features'] = 'nested-attributes'
        self.combined_xes.attrib['openxes.version'] = '1.0RC7'

        i = 0
        # TODO remove files in input directory + combined xes
        for filename in os.listdir(const.XES_FILES_DIR):  # only for testing
            if ".xes" in filename:
                path = os.path.join(const.XES_FILES_DIR, filename)
                self.add_traces(path)
                i += 1
                print(i)
                # if i > 1000:
                # break

        # continuously monitor xes_files folder
        # input_handler = self.InputHandler()
        # observer = Observer()
        # observer.schedule(
        #     input_handler, path=const.XES_FILES_DIR, recursive=False)
        # observer.start()

        # keep the program running
        # try:
        #     while True:
        #         time.sleep(1)
        # except KeyboardInterrupt:
        #     observer.stop()

        # observer.join()


if __name__ == '__main__':
    fm = FileMerger()
    fm.start()
