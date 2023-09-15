# Dogecoin Blockchain Address Sync (DBAS)

**Dogecoin Blockchain Address Sync (DBAS)** is a powerful tool designed to extract address balances directly from the Dogecoin blockchain and store them into MongoDB for efficient queries. This Python script is tailored for those who want to maintain a record of Dogecoin balances without relying on third-party services.

## Features:

- **Fast Synchronization**: Sync all active Dogecoin addresses with their respective balances.
- **Multiprocessing Support**: Take advantage of multiple CPU cores for accelerated synchronization. The number of cores can be specified for fine-tuned performance.
- **Direct JSON-RPC Calls**: For accurate and real-time data extraction without third-party dependencies.

## Prerequisites:

1. **Dogecoin CLI**: Ensure that the Dogecoin command-line interface is installed and properly set up on your system.
2. **RPC Node**: The script communicates with the Dogecoin blockchain using RPC calls. Ensure your RPC node is running and accessible.
3. **MongoDB**: This script uses MongoDB as its database. Ensure you have MongoDB installed and running.

## Quick Start:

1. **Clone the repository**:
```bash
git clone https://github.com/Iamparsa/DogeCoinDBSync.git
cd DogeCoinDBSync
```
2. **Install the required Python libraries**:
```bash
pip install -r requirements.txt
```
3. **Configure**:
Edit the `config.json` file and set your RPC credentials, MongoDB settings, and desired number of cores. Here's a sample structure:

```json
{
    "mongodb_host": "YOUR_MONGODB_USER",
    "mongodb_port": 27017,
    "mongodb_database_name": "YOUR_MONGODB_DATABASE_NAME",
    "rpc_user": "YOUR_RPC_USER",
    "rpc_password": "YOUR_RPC_PASSWORD",
    "rpc_host": "YOUR_RPC_HOST",
    "rpc_port": 20075
}
```

4. **Run the script**:
```bash
python sync.py --cores <number_of_cores>
```
By default, after the initial fast synchronization using multiple cores, the script will shift to a standard sync mode to listen for new blocks and address changes.

## Development:

- **Configurations**: All necessary configurations like RPC credentials, MongoDB settings, and number of cores are present in `config.json`. Adjust them as per your setup.
  
- **Data Structure**: As of now, the tool only stores the address balance. It doesn't store full block or transaction details. If you're looking to expand on this, consider modifying the `sync.py` script.
  
- **Resuming**: Currently, the script doesn't support resuming. Due to the use of multiprocessing, if the script crashes or is forcibly stopped, some blocks might not have been processed. In such cases, it's recommended to start the script from scratch or from a known block height.

## Note:
This project is under active development. There might be changes and enhancements in the future. Ensure you keep your fork or local clone updated.

### ☕️ Support & Donations

Developing and maintaining projects like this take up a lot of time and energy. If you find this project useful, and want to see more features or improvements, consider supporting its development. Even the smallest gesture can be a big motivation boost.

**Buy me a coffee:**

```
Dogecoin Wallet Address: DQNXRYQpPzbCSknniBKzSgZvqJxCJEs2Ap
```

Your support helps in keeping the project alive and kicking, allowing me to spend more time perfecting and evolving it. Thank you in advance for any support you can offer!

## Contribution:

Contributions are welcomed! If you find any bugs, have feature requests, or want to contribute to the code, feel free to open an issue or a pull request.

## Disclaimer:

This tool is provided "as is" without any warranties. Always ensure you have backups and use it at your own risk.

## License:

[MIT License](LICENSE)

## Keywords:

Dogecoin, Blockchain, Sync, Address, Balance, MongoDB, RPC, Python, Script, Tool, Database, Multiprocessing

---