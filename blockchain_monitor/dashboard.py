import data_processor as dp


class Dashboard():
    def __init__(self) -> None:
        self.current_block_number = 0
        self.current_block_timestamp = 0
        self.block_stats = {}
        self.sender_stats = {}
        self.receiver_stats = {}
        self.petri_net_path = ""
        self.bpmn_diagram_path = ""

    # TODO called when underlying xes_file changes or when the user selects a new option
    def update(self):
        current_block_stats = dp.get_current_block_stats()
        self.current_block_number = current_block_stats['current_block_number']
        self.current_block_timestamp = current_block_stats['current_block_timestamp']
        self.block_stats = dp.get_block_stats()
        self.sender_stats = dp.get_sender_stats(
            0, self.current_block_number)  # TODO use dynamic block ranges
        self.receiver_stats = dp.get_receiver_stats(
            0, self.current_block_number)
        self.petri_net_path = dp.get_petri_net(0, self.current_block_number)
        self.bpmn_diagram_path = dp.get_bmpn_diagram(
            0, self.current_block_number)
