import subprocess
import multiprocessing
from test_app import file_feeder
import constants as const


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
    # TODO either launch at start up or by user request
    # reader_process = multiprocessing.Process(target=file_reader.read_in)
    # reader_process.start()
    return


def launch_file_feeder():
    # feeder_process = multiprocessing.Process(target=file_feeder.feed_files(300))
    # feeder_process.start()
    return


def launch_blf():
    return


def reset_application():
    # TODO think about remove all files in 'xes_files' before running app
    # delete all gathered data
    return


def set_input_mode():
    # Streaming BLF
    # Streaming Test Data
    # Static Test Data
    return


if __name__ == '__main__':
    # TODO launch file merger
    from webapp import app
    app.run(debug=True)
