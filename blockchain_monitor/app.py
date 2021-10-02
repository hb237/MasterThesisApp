import subprocess
import multiprocessing
from test_app import file_feeder
import file_merger
import constants as const

feeder_process = None
merger_process = None


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
        msg = 'An error occurred during BLF validation.'
    return msg


def extract_current_manifest():
    msg = ""
    try:
        msg = subprocess.check_output(
            ['java', '-jar', const.BLF_JAR_PATH, const.BLF_EXTRACT, const.MANIFEST_PATH])
    except subprocess.CalledProcessError as e:
        msg = 'An error occurred during BLF exctraction.'
    return msg


def launch_file_merger():
    global merger_process

    if merger_process is not None:
        merger_process.terminate()

    merger_process = multiprocessing.Process(target=file_merger.read_in)
    merger_process.start()


def launch_file_feeder(speed: int):
    global feeder_process

    if feeder_process is not None:
        feeder_process.terminate()

    feeder_process = multiprocessing.Process(
        target=file_feeder.feed_files(speed))
    feeder_process.start()


def reset_application():
    # TODO think about remove all files in 'xes_files' before running app
    return


def set_input_mode():

    # Streaming BLF
    # Streaming Test Data
    # Static Test Data
    return


if __name__ == '__main__':
    # launch_file_merger()
    from webapp import app
    app.run(debug=True)
