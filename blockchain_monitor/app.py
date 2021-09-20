import subprocess
import multiprocessing
import file_reader
import file_processor
import dashboard
import constants as const

if __name__ == '__main__':
    processes = []

    # Validate BLF manifest
    try:
        print(subprocess.check_output(['java', '-jar', const.BLF_JAR_PATH, const.BLF_VALIDATE, './blf/manifests/cryptokitties.bcql']))
    except subprocess.CalledProcessError as e:
        print('An error occured during BLF validation.')

    # Create processes for file reader,  processor and dashboard
    reader_process = multiprocessing.Process(target=file_reader.read_in)
    processor_process = multiprocessing.Process(target=file_processor.process_data)
    dashboard_process = multiprocessing.Process(target=dashboard.visualize)
    
    # Collect processes
    processes.append(reader_process)
    processes.append(processor_process)
    processes.append(dashboard_process)

    # Start all proccesses
    for p in processes:
        p.start()

    # Start file feeder or start BLF extraction
    