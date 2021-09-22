import subprocess
import multiprocessing
from test_app import file_feeder
import file_reader
import constants as const

if __name__ == '__main__':
    #TODO think about remove all files in 'xes_files' before running app

    # # Validate BLF manifest
    # try:
    #     print(subprocess.check_output(['java', '-jar', const.BLF_JAR_PATH, const.BLF_VALIDATE, './blf/manifests/cryptokitties.bcql']))
    # except subprocess.CalledProcessError as e:
    #     print('An error occured during BLF validation.')

    # # Create processes for file reader TODO dashboard
    # reader_process = multiprocessing.Process(target=file_reader.read_in)
    # reader_process.start()

    # # Start file feeder or start BLF extraction
    # feeder_process = multiprocessing.Process(target=file_feeder.feed_files(300))
    # feeder_process.start()

    from webapp import app
    app.run(debug=True)