# Keep in mind that lxml supports only xPath 1.0
import time
import os
import lxml.etree as ET
from lxml.etree import Element
from data_transformer import DataTransformer
import constants as const


class FileMerger():
    def __init__(self) -> None:
        # TODO set parameters
        self.combined_xes = None
        self.last_blk = None
        self.first_blk = None
        self.max_block_range = 500
        self.proccessed_files = []

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

        with open(const.XES_FILES_COMBINED_PATH, 'wb') as f:
            print('Combined XES was extended by: ' + path)
            f.write(ET.tostring(self.combined_xes, pretty_print=True))

    def remove_old_events(self, block_nr: int):
        for event in self.combined_xes.iter('event'):
            if int(event.find(".//int[@key='tx_blocknumber']").get('value')) <= block_nr:
                event.getparent().remove(event)
        for trace in self.combined_xes.iter('trace'):
            if(trace.find(".//event") is None):
                trace.getparent().remove(trace)

    def merge(self):
        print('Started file reader.')

        # setup xes log structure
        self.combined_xes = Element('log')
        self.combined_xes.attrib['xes.version'] = '1.0'
        self.combined_xes.attrib['xes.features'] = 'nested-attributes'
        self.combined_xes.attrib['openxes.version'] = '1.0RC7'

        while True:  # TODO add waiting time
            time.sleep(1)
            current_files = os.listdir(const.XES_FILES_DIR)
            unprocessed_files = list(
                set(current_files) - set(self.proccessed_files))
            for file_name in unprocessed_files:
                self.add_traces(os.path.join(const.XES_FILES_DIR, file_name))
                self.proccessed_files.append(file_name)
