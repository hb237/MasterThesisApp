from web3 import Web3
from datetime import datetime


def get_current_block_stats() -> dict:
    # TODO launch geth client with:
    # TODO set constants
    # TODO set --datadir appropriately
    # geth --syncmode "light" --ws --ws.addr 127.0.0.1 --ws.port 8546 --datadir="/media/hendrik/SSD-1TB/geth"
    result = None
    try:
        w3 = Web3(Web3.WebsocketProvider('ws://127.0.0.1:8546'))
        current_block_number = int(w3.eth.get_block_number())
        current_block_timestamp = datetime.utcfromtimestamp(int(w3.eth.getBlock(
            current_block_number).timestamp)).strftime('%Y-%m-%d %H:%M:%S UTC+0')
        result = {'current_block_number': current_block_number,
                  'current_block_timestamp': current_block_timestamp}
    finally:
        return result
