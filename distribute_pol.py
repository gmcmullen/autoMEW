from web3 import Web3
import json
from datetime import datetime
import os
import argparse
import glob
from typing import List, Dict, Any
from contextlib import contextmanager

# Constants
POLYGON_RPC_URL = 'https://polygon-rpc.com'
POLYGON_CHAIN_ID = 137
GAS_LIMIT = 21000
PRIVATE_KEY_FILE = 'privatekey.txt'
WALLET_FILE_PATTERN = 'all_wallets_*.json'

# Connect to Polygon network
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))
if not w3.is_connected():
    raise ConnectionError("Failed to connect to Polygon network")

def get_latest_wallets_file() -> str:
    """Find and return the most recent wallet file.
    
    Returns:
        str: Path to the latest wallet file
        
    Raises:
        ValueError: If no wallet files are found
    """
    wallet_files = glob.glob(WALLET_FILE_PATTERN)
    if not wallet_files:
        raise ValueError("No all_wallets_*.json files found")
    
    latest_file = max(wallet_files, key=os.path.getctime)
    print(f"Using latest wallet file: {latest_file}")
    return latest_file

def load_private_key() -> str:
    """Load and validate the sender's private key.
    
    Returns:
        str: The validated private key
        
    Raises:
        ValueError: If the private key file is not found or invalid
    """
    try:
        with open(PRIVATE_KEY_FILE, 'r') as f:
            private_key = f.read().strip()
            private_key = ''.join(private_key.split())
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            if len(private_key) != 66:  # '0x' + 64 hex chars
                raise ValueError(f"Invalid private key length: {len(private_key)} chars (expected 66)")
            return private_key
    except FileNotFoundError:
        raise ValueError("privatekey.txt file not found. Please create this file with your private key.")

@contextmanager
def create_log_file(test_mode: bool) -> Any:
    """Create and manage a log file for the distribution process.
    
    Args:
        test_mode: Whether the script is running in test mode
        
    Yields:
        file: The log file object
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'pol_distribution_log_{timestamp}.txt'
    
    with open(log_filename, 'w') as log_file:
        log_file.write(f"POL Distribution Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        yield log_file
    
    print(f"\n{'Simulation' if test_mode else 'Distribution'} complete! Check {log_filename} for detailed logs.")

def log_transaction_details(log_file: Any, sender_address: str, sender_balance: int, 
                          gas_price: int, total_gas: int, total_per_transaction: int, 
                          total_needed: int, test_mode: bool, latest_file: str,
                          amount: float) -> None:
    """Log transaction details to the log file.
    
    Args:
        log_file: The log file object
        sender_address: The sender's address
        sender_balance: The sender's balance in wei
        gas_price: The gas price in wei
        total_gas: The total gas cost in wei
        total_per_transaction: The total cost per transaction in wei
        total_needed: The total amount needed for all transactions in wei
        test_mode: Whether the script is running in test mode
        latest_file: The wallet file being used
        amount: Amount of POL to send to each wallet
    """
    log_file.write(f"Sender Address: {sender_address}\n")
    log_file.write(f"Sender Balance: {Web3.from_wei(sender_balance, 'ether')} POL\n")
    log_file.write(f"Amount per wallet: {amount} POL\n")
    log_file.write(f"Gas Price: {Web3.from_wei(gas_price, 'gwei')} Gwei\n")
    log_file.write(f"Gas Limit: {GAS_LIMIT}\n")
    log_file.write(f"Gas Cost per transaction: {Web3.from_wei(total_gas, 'ether')} POL\n")
    log_file.write(f"Total per transaction: {Web3.from_wei(total_per_transaction, 'ether')} POL\n")
    log_file.write(f"Total needed: {Web3.from_wei(total_needed, 'ether')} POL\n")
    log_file.write(f"Test Mode: {'Yes' if test_mode else 'No'}\n")
    log_file.write(f"Using wallet file: {latest_file}\n\n")

def validate_amount(amount: float) -> None:
    """Validate the POL amount to distribute.
    
    Args:
        amount: Amount of POL to send to each wallet
        
    Raises:
        ValueError: If amount is None or less than or equal to zero
    """
    if amount is None:
        raise ValueError("Amount must be specified")
    if amount <= 0:
        raise ValueError("Amount must be greater than 0 POL")

def distribute_pol(test_mode: bool = False, amount: float = None) -> None:
    """Distribute POL tokens to multiple wallets.
    
    Args:
        test_mode: If True, simulate transactions without sending
        amount: Amount of POL to send to each wallet
    """
    # Load and validate private key
    sender_private_key = load_private_key()
    
    # Load recipient addresses
    latest_file = get_latest_wallets_file()
    with open(latest_file, 'r') as f:
        wallets_data = json.load(f)
        recipient_addresses = [wallet['public_key'] for wallet in wallets_data]

    # Calculate amounts
    amount_wei = Web3.to_wei(amount, 'ether')
    sender_address = w3.eth.account.from_key(sender_private_key).address
    nonce = w3.eth.get_transaction_count(sender_address)
    sender_balance = w3.eth.get_balance(sender_address)
    gas_price = w3.eth.gas_price
    total_gas = gas_price * GAS_LIMIT
    total_per_transaction = amount_wei + total_gas
    total_needed = total_per_transaction * len(recipient_addresses)

    # Print initial information
    print(f"\nSender balance: {Web3.from_wei(sender_balance, 'ether')} POL")
    print(f"\nAmount per transaction:")
    print(f"  POL to send: {amount} POL")
    print(f"  Gas price: {Web3.from_wei(gas_price, 'gwei')} Gwei")
    print(f"  Gas limit: {GAS_LIMIT}")
    print(f"  Gas cost: {Web3.from_wei(total_gas, 'ether')} POL")
    print(f"  Total per transaction: {Web3.from_wei(total_per_transaction, 'ether')} POL")
    print(f"\nTotal needed for all transactions: {Web3.from_wei(total_needed, 'ether')} POL")

    if sender_balance < total_needed:
        raise ValueError(f"Insufficient balance. Need {Web3.from_wei(total_needed, 'ether')} POL but have {Web3.from_wei(sender_balance, 'ether')} POL")

    # Process transactions
    with create_log_file(test_mode) as log_file:
        log_transaction_details(log_file, sender_address, sender_balance, gas_price, 
                             total_gas, total_per_transaction, total_needed, 
                             test_mode, latest_file, amount)

        for i, recipient in enumerate(recipient_addresses, 1):
            try:
                transaction = {
                    'from': sender_address,
                    'to': Web3.to_checksum_address(recipient),
                    'value': amount_wei,
                    'nonce': nonce,
                    'gas': GAS_LIMIT,
                    'gasPrice': gas_price,
                    'chainId': POLYGON_CHAIN_ID
                }

                if test_mode:
                    log_message = f"Wallet {i}: Would send {amount} POL to {recipient}\n"
                    log_message += f"Gas Price: {Web3.from_wei(transaction['gasPrice'], 'gwei')} Gwei\n"
                    log_message += f"Gas Limit: {transaction['gas']}\n"
                    log_message += f"Total cost: {Web3.from_wei(total_per_transaction, 'ether')} POL\n"
                else:
                    signed_txn = w3.eth.account.sign_transaction(transaction, sender_private_key)
                    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
                    log_message = f"Wallet {i}: Successfully sent {amount} POL to {recipient}\nTransaction Hash: {receipt['transactionHash'].hex()}\n"
                
                print(log_message)
                log_file.write(log_message)
                nonce += 1
                
            except Exception as e:
                error_message = f"Wallet {i}: Failed to send POL to {recipient}\nError: {str(e)}\n"
                print(error_message)
                log_file.write(error_message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Distribute POL tokens to multiple wallets')
    parser.add_argument('--test', action='store_true', help='Run in test mode (simulate transactions without sending)')
    parser.add_argument('--amount', type=float, required=True, help='Amount of POL to send to each wallet')
    args = parser.parse_args()
    
    try:
        validate_amount(args.amount)
        distribute_pol(test_mode=args.test, amount=args.amount)
    except ValueError as e:
        print(f"\nError: {str(e)}")
        print("\nUsage example:")
        print("  python distribute_pol.py --amount 0.25 [--test]")
        exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
        exit(1) 