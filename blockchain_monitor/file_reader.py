# Keep in mind that lxml supports only xPath 1.0
#from web3 import Web3
#w3 = Web3(Web3.WebsocketProvider('wss://mainnet.infura.io/ws/v3/bcf5331eacae4b0c8fba1751b28c6768'))
from data_processor import DataProcessor
import lxml.etree as ET
from lxml.etree import Element
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent, FileSystemEventHandler
import constants as const


def add_traces(path: str, dp: DataProcessor):
    # read in new xes file as tree
    tree = None
    attempts = 0
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

    for new_trace in root.iter('trace'):
        new_trace_piid = new_trace.find(".//string[@key='ident:piid']").get('value')
        existing_piids = dp.combined_log.findall(".//string[@key='ident:piid']")

        trace = None
        for ep in existing_piids:
            if(ep.get('value') == new_trace_piid):
                trace = ep.find("..")

        if(trace == None):
            dp.combined_log.append(new_trace)
        else:
            new_events = new_trace.findall(".//event")
            for event in new_events:
                trace.append(event)

    dp.process_data()




class InputHandler(FileSystemEventHandler):
    def __init__(self, dp: DataProcessor) -> None:
        super().__init__()
        self.dp = dp

    # Once BLF extracted a XES file from a new block write its trace to the combined log.
    def on_created(self, event):
        if type(event) == FileCreatedEvent:
            print('continuous')
            add_traces(event.src_path, self.dp)

def read_in():
    print('Started file reader.')

    dp = DataProcessor()

    # setup xes log structure
    dp.combined_log = Element('log')
    dp.combined_log.attrib['xes.version'] = '1.0'
    dp.combined_log.attrib['xes.features'] = 'nested-attributes'
    dp.combined_log.attrib['openxes.version'] = '1.0RC7'

    # read in already existing files in xes_files folder # TODO do I need that or should I delete it + file in xes_files_combined
    for filename in os.listdir(const.XES_FILES_DIR):
        if ".xes" in filename:
            path = os.path.join(const.XES_FILES_DIR, filename)
            add_traces(path, dp)

    # continuously monitor xes_files folder
    input_handler = InputHandler(dp)
    observer = Observer()
    observer.schedule(input_handler, path=const.XES_FILES_DIR, recursive=False)
    observer.start()

    # keep the programm running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()


if __name__ == '__main__':
    read_in()