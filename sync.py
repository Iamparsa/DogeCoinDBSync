import requests
import json
import logging
import argparse
import pymongo
from pymongo import errors
from multiprocessing import Pool, cpu_count
from time import sleep

# RPC and DB configurations
# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

RPC_URL = f"http://{config['rpc_host']}:{config['rpc_port']}"
RPC_USER = config['rpc_user']
RPC_PASS = config['rpc_password']
DB_URL = f"mongodb://{config['mongodb_host']}:{config['mongodb_port']}/"
DB_NAME = config["mongodb_database_name"]

logging.basicConfig(level=logging.INFO)

client = pymongo.MongoClient(DB_URL)
db = client[DB_NAME]


# Create Database Schema
if 'addresses' not in db.list_collection_names():
    db.create_collection('addresses')

if 'blocks' not in db.list_collection_names():
    db.create_collection('blocks')

db['addresses'].create_index([('address', pymongo.ASCENDING)], unique=True)

db['blocks'].create_index([('block', pymongo.ASCENDING)], unique=True)

def parse_rpc_response(response):
    try:
        return json.loads(response)
    except ValueError:
        logging.error(f"Failed to parse RPC response: {response}")
        return None
    
def rpc_call(method, params=[]):
    headers = {'content-type': 'application/json'}
    data = {
        "jsonrpc": "2.0",
        "id": "rpc_call",
        "method": method,
        "params": params
    }
    response = requests.post(RPC_URL, auth=(RPC_USER, RPC_PASS), headers=headers, json=data)
    # logging.info(f"RPC Response for {method}: {response.text}")
    
    if response.status_code != 200:
        logging.error(f"RPC error ({method}): {response.content}")
        return None
    
    response_json = response.json()
    if 'error' in response_json and response_json['error']:
        logging.error(f"RPC error ({method}): {response_json['error']}")
        return None

    return response_json['result']

def process_address(address, amount, is_input):
    entry = db.addresses.find_one({"address": address})
    if not entry:
        if is_input:
            db.addresses.insert_one({"address": address, "balance": -amount, "total_received": 0})
        else:
            db.addresses.insert_one({"address": address, "balance": amount, "total_received": amount})
    else:
        if is_input:
            db.addresses.update_one({"address": address}, {"$inc": {"balance": -amount}})
        else:
            db.addresses.update_one({"address": address}, {"$inc": {"balance": amount, "total_received": amount}})

def worker(block_height):
    block_hash = rpc_call("getblockhash", [block_height])
    block = rpc_call("getblock", [str(block_hash), True])
    if not block:
        logging.error(f"Failed to fetch block data for height {block_height}.")
        return

    for txid in block['tx']:
        try:
            raw_tx = rpc_call("getrawtransaction", [txid])
            if not raw_tx:
                logging.error(f"Failed to fetch raw transaction data for txid {txid}.")
                continue
            
            tx = rpc_call("decoderawtransaction", [raw_tx])
            if not tx or 'vin' not in tx:
                logging.error(f"Failed to decode transaction data for txid {txid}.")
                continue

            for vin in tx['vin']:
                if 'txid' in vin:
                    raw_prev_tx = rpc_call("getrawtransaction", [vin['txid']])
                    if not raw_prev_tx:
                        logging.error(f"Failed to fetch raw transaction data for txid {vin['txid']}.")
                        continue
                    
                    prev_tx = rpc_call("decoderawtransaction", [raw_prev_tx])
                    if not prev_tx or 'vout' not in prev_tx:
                        logging.error(f"Failed to decode transaction data for txid {vin['txid']}.")
                        continue

                    prev_output = prev_tx['vout'][vin['vout']]
                    address = prev_output['scriptPubKey']['addresses'][0]
                    amount = prev_output['value']
                    process_address(address, amount, True)
        except KeyError:
            logging.error(f"Expected key not found while processing txid {txid}. Data: {tx}")
        except Exception as e:
            logging.error(f"Unexpected error while processing txid {txid}: {e}")
            continue

    
        try:
            for vout in tx['vout']:
                # For outputs, credit the amount to the address
                address = vout['scriptPubKey']['addresses'][0]
                amount = vout['value']
                process_address(address, amount, False)
        except KeyError:
            logging.error(f"'vout' key not found in tx")
            continue

    db.blocks.insert_one({"height": block_height, "hash": block_hash})
    logging.info(f"Processed block {block_height}")


def get_latest_synced_block():
    latest_block = db.blocks.find_one(sort=[("height", pymongo.DESCENDING)])
    return latest_block["height"] if latest_block else 0

def check_chain_reorg():
    last_known_block = db.blocks.find_one(sort=[("height", pymongo.DESCENDING)])
    if last_known_block:
        block_hash = rpc_call("getblockhash", [last_known_block['height']])
        if block_hash != last_known_block['hash']:
            logging.warning("Chain reorg detected!")
            db.blocks.delete_many({"height": {"$gte": last_known_block['height']}})
            return True
    return False

def main():
    parser = argparse.ArgumentParser(description="Sync Dogecoin blockchain data to MongoDB.")
    parser.add_argument("--cores", type=int, default=1, help="Number of cores for multiprocessing.")
    args = parser.parse_args()

    while True:
        try:
            latest_blockchain_block = rpc_call("getblockcount")

            latest_synced_block = get_latest_synced_block()

            if latest_synced_block < latest_blockchain_block:
                if args.cores > 1 and (latest_blockchain_block - latest_synced_block) > 10:
                    logging.info("Fast syncing using {} cores...".format(args.cores))

                    with Pool(args.cores) as pool:
                        pool.map(worker, range(latest_synced_block + 1, latest_blockchain_block + 1))
                else:
                    logging.info("Normal syncing...")

                    worker(latest_synced_block + 1)
            elif check_chain_reorg():
                continue
            else:
                logging.info("Waiting for new blocks...")
                sleep(60)
        except Exception as e:
            logging.error("Error encountered: {}. Retrying...".format(e))
            sleep(10)

if __name__ == "__main__":
    main()

