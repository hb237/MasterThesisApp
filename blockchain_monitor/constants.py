XES_FILES_DIR = './xes_files'
XES_FILES_COMBINED_PATH = './xes_files_combined/combined_log.xml'
XES_FILES_COMBINED_PATH_TEST = './xes_files_combined/combined_log_TEST.xml'  # TODO remove
BLF_JAR_PATH = './blf/blf-cmd.jar'
BLF_VALIDATE = 'validate'
BLF_EXTRACT = 'extract'
TEST_FILES_LOCATION = './test_app/test_files'
TEST_FILES_DESTINATION = "./xes_files"
MANIFEST_PATH = 'static/user_uploads/manifest.bcql'
BPMN_PATH = 'static/user_uploads/diagram.bpmn'
BPMN_EMPTY_PATH = 'static/empty-diagram.bpmn'
ALLOWED_MANIFEST_EXTENSIONS = {'txt', 'bcql'}
ALLOWED_BPMN_EXTENSIONS = {'xml', 'bpmn'}
SETTINGS_PATH = 'static/user_uploads/settings.json'

# Do not add './' to the front.
MONITORING_DATA_DIR = 'static/monitoring_data/'
PETRI_NET = MONITORING_DATA_DIR + 'petri_net.png'
BPMN_DIAGRAM = MONITORING_DATA_DIR + 'bpmn_diagram.png'
BPMN_COSTS_DIAGRAM = MONITORING_DATA_DIR + 'bpmn_costs_diagram.png'
DFG_FREQUENCY = MONITORING_DATA_DIR + 'dfg_frequency.png'
DFG_PERFORMANCE = MONITORING_DATA_DIR + 'dfg_performance.png'
EVENTS = MONITORING_DATA_DIR + 'events.json'
TRACES = MONITORING_DATA_DIR + 'traces.json'
CURRENT_BLOCK_STATS = MONITORING_DATA_DIR + 'current_block_stats.json'
BLOCK_STATS = MONITORING_DATA_DIR + 'block_stats.json'
SENDER_STATS = MONITORING_DATA_DIR + 'sender_stats.json'
RECEIVER_STATS = MONITORING_DATA_DIR + 'receiver_stats.json'
ETH_RATES = MONITORING_DATA_DIR + 'eth_rates.json'
DATASET_LAST_UPDATE = MONITORING_DATA_DIR + 'dataset_last_update.json'
CONFORMANCE_CHECKING_RESULTS = MONITORING_DATA_DIR + \
    'conformance_checking_results.json'
