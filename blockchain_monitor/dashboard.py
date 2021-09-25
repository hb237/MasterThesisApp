import blockchain_connector as bc
from data_processor import DataProcessor


class Dashboard():
    def __init__(self) -> None:
        self.current_block_number = 0
        self.current_block_timestamp = 0
        self.block_stats = {}
        self.sender_stats = {}
        self.receiver_stats = {}
        self.petri_net_path = ""
        self.bpmn_diagram_path = ""
        self.dfg_frequency_path = ""
        self.dfg_performance_path = ""
        self.bpmn_diagram_with_costs_path = ""
        self.eth_rates = {}

    # TODO called when underlying xes_file changes or when the user selects a new option
    # TODO use variables from_block and  to_block, perhaps use ENUM for most current block
    # TODO only execute the visible modules, add visibility flag
    # TODO what about mutliple users
    # TODO save settings as cookie
    def update(self):
        # TODO delete old visualizations
        # TODO perhaps do not store images only send them out
        cbs = bc.get_current_block_stats()
        self.current_block_number = cbs['current_block_number']
        self.current_block_timestamp = cbs['current_block_timestamp']
        # TODO use from_block, to_block
        dp = DataProcessor(0, self.current_block_number)
        # self.block_stats = dp.get_block_stats()
        # self.sender_stats = dp.get_sender_stats()
        # self.receiver_stats = dp.get_receiver_stats()
        # self.petri_net_path = dp.get_petri_net()
        # self.bpmn_diagram_path = dp.get_bmpn_diagram()
        # self.dfg_frequency_path = dp.get_dfg_frequency()
        # self.dfg_performance_path = dp.get_dfg_performance()
        # self.eth_rates = dp.get_eth_rates()
        # eth_to_eur = self.eth_rates.get('EUR')
        # self.bpmn_diagram_with_costs_path = dp.get_bpmn_diagram_with_costs(
        #     'EUR', eth_to_eur)
        # dp.get_events()
        # dp.conformance_checking()

        # price fo different tasks over time
