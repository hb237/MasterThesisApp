from web3 import Web3
from datetime import datetime
import constants as const
import json


def get_current_block_stats() -> dict:
    with open(const.SETTINGS_PATH) as json_file:
        config = json.loads(json_file.read())

    geth_ip = str(config.get('inputGethIP', '127.0.0.1'))
    geth_port = int(config.get('inputGethPort', 8546))

    # launch geth client with:
    # geth --syncmode "light" --ws --ws.addr 127.0.0.1 --ws.port 8546 --datadir="/media/hendrik/SSD-1TB/geth"
    result = None
    try:
        ws_connection_string = 'ws://' + geth_ip + ':' + geth_port
        w3 = Web3(Web3.WebsocketProvider(ws_connection_string))
        current_block_number = int(w3.eth.get_block_number())
        current_block_timestamp = datetime.utcfromtimestamp(int(w3.eth.getBlock(
            current_block_number).timestamp)).strftime('%Y-%m-%d %H:%M:%S UTC+0')
        result = {'current_block_number': current_block_number,
                  'current_block_timestamp': current_block_timestamp}
    finally:
        return result
