import os
import sys
import time
import lxml.etree as ET
from lxml.etree import Element
from shutil import copy
import constants as const




def get_time(path: str) -> int:
    tree = ET.parse(path)
    root = tree.getroot()
    timestamp = int(root.find(".//event[1]/int[@key='block_timestamp']").get('value'))
    return timestamp

def feed_files(speed: int):
    print('Started file feeder.')
    print('Start feeding files with speed: ' + str(speed))

    prev_block_time = -1

    # move files one by one
    for filename in sorted(os.listdir(const.TEST_FILES_LOCATION)):
        if ".xes" in filename:
            filepath = os.path.join(const.TEST_FILES_LOCATION, filename)
            current_block_time = get_time(filepath)
            waiting_time = 0
            if prev_block_time > -1:
                waiting_time = (current_block_time - prev_block_time) / speed
            print('sleep for ' + str(waiting_time) + ' seconds')
            time.sleep(waiting_time)
            prev_block_time = current_block_time
            copy(filepath, const.TEST_FILES_DESTINATION)
            print('copied ' + filepath)

if __name__ == '__main__':
    speed = 1
    if (len(sys.argv) > 1):
        try:
            speed = int(sys.argv[1])
        except ValueError:
            print('arg must be int')
            exit()

    feed_files(speed)