import subprocess
import multiprocessing
from test_app import file_feeder
import constants as const


def save_bpmn_model(bpmn_model):
    # bpmn modul MUST ONLY contain
    # Events (start / end events)
    # Tasks
    # Gateways (exclusive, parallel, inclusive)
    return


def save_manifest_file(mainfest):
    return


def set_input_src(type, speed):
    # type : feeder, blf
    # speed of file feeder
    # either file feeder or blf
    return


def validate_current_manifest():
    msg = ""
    try:
        msg = subprocess.check_output(
            ['java', '-jar', const.BLF_JAR_PATH, const.BLF_VALIDATE, const.MANIFEST_PATH])
    except subprocess.CalledProcessError as e:
        msg = 'An error occured during BLF validation.'
    return msg


def launch_file_reader():
    return


def launch_file_feeder():
    return


def launch_blf():
    return


def reset_application():
    # delete all gathered data
    return


def set_input_mode():
    # Streaming BLF
    # Streaming Test Data
    # Static Test Data
    return


if __name__ == '__main__':
    # TODO think about remove all files in 'xes_files' before running app

    # # Create processes for file reader TODO dashboard
    # reader_process = multiprocessing.Process(target=file_reader.read_in)
    # reader_process.start()

    # # Start file feeder or start BLF extraction
    # feeder_process = multiprocessing.Process(target=file_feeder.feed_files(300))
    # feeder_process.start()

    from webapp import app
    app.run(debug=True)
