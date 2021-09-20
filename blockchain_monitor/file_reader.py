# Keep in mind that lxml supports only xPath 1.0
import lxml.etree as ET
from lxml.etree import Element
from lxml.etree import ElementTree
import os
import time
from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent, FileSystemEventHandler
import constants as const
#from web3 import Web3

#w3 = Web3(Web3.WebsocketProvider('wss://mainnet.infura.io/ws/v3/bcf5331eacae4b0c8fba1751b28c6768'))

def merge_trace(new_trace: Element, log: Element):
    new_trace_piid = new_trace.find(".//string[@key='ident:piid']").get('value')
    existing_piids = log.findall(".//string[@key='ident:piid']")

    trace = None
    for ep in existing_piids:
        if(ep.get('value') == new_trace_piid):
            trace = ep.find("..")

    if(trace == None):
        log.append(new_trace)
    else:
        new_events = new_trace.findall(".//event")
        for event in new_events:
            trace.append(event)

def add_traces(path: str, log: Element):
    tree = ET.parse(path)
    root = tree.getroot()

    for trace in root.iter('trace'):
        merge_trace(trace, log)

    with open(const.XES_FILES_COMBINED_PATH, 'wb') as f:
        tree = ElementTree(log)
        tree.write(f)

class InputHandler(FileSystemEventHandler):
    def __init__(self, combined_log) -> None:
        super().__init__()
        self.combined_log = combined_log

    # Once BLF extracted a XES file from a new block write its trace to the combined log.
    def on_created(self, event):
        if type(event) == FileCreatedEvent:
                add_traces(event.src_path, self.combined_log)

def read_in():
    print('Started file reader.')

    # setup xes log structure
    combined_log = Element('log')
    combined_log.attrib['xes.version'] = '1.0'
    combined_log.attrib['xes.features'] = 'nested-attributes'
    combined_log.attrib['openxes.version'] = '1.0RC7'

    # read in already existing files in xes_files folder
    for filename in os.listdir(const.XES_FILES_DIR):
        if ".xes" in filename:
            path = os.path.join(const.XES_FILES_DIR, filename)
            add_traces(path, combined_log)

    # save log to file
    with open(const.XES_FILES_COMBINED_PATH, 'wb') as f:
        tree = ElementTree(combined_log)
        tree.write(f)

    # continuously monitor xes_files folder
    input_handler = InputHandler(combined_log)
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