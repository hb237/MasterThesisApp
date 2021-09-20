from watchdog.observers import Observer
from watchdog.events import FileCreatedEvent, FileModifiedEvent, FileSystemEventHandler
import time
import constants as const
import os
class InputHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if type(event) == FileModifiedEvent:
            print("combined log modified")
            pass


def process_data():
    print('Started file processor.')

    # create combined log file if it does not exist yet
    if not os.path.exists(const.XES_FILES_COMBINED_PATH):
        os.mknod(const.XES_FILES_COMBINED_PATH)

    # continuously monitor combined xes files
    input_handler = InputHandler()
    observer = Observer()
    observer.schedule(input_handler, path=const.XES_FILES_COMBINED_PATH, recursive=False)
    observer.start()

    # keep the programm running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()


if __name__ == '__main__':
    process_data()