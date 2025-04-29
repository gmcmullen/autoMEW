# AutoMEW - Automated Polygon Wallet Distribution

AutoMEW is a Python-based tool for automating the distribution of POL (Polygon) tokens to multiple wallet addresses. It provides functionality for both creating new wallets and distributing tokens to them in a secure and efficient manner.

## Features

- **Wallet Generation**: Create multiple Ethereum-compatible wallets with private keys and mnemonic phrases
- **Batch Distribution**: Send POL tokens to multiple addresses in one operation
- **Test Mode**: Simulate transactions before sending real funds
- **Detailed Logging**: Comprehensive transaction logs with gas estimates and costs
- **PDF Export**: Generate printable PDF cards containing wallet details
- **Input Validation**: Robust error handling and input validation

## Prerequisites

- Python 3.6 or higher
- Web3.py library
- Access to Polygon network (via RPC endpoint)
- Sufficient POL balance in sender's wallet

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AutoMEW.git
   cd AutoMEW
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `privatekey.txt` file containing your sender wallet's private key:
   ```bash
   echo "your_private_key_here" > privatekey.txt
   ```
   **Important**: Keep your private key secure and never share it with anyone.

## Usage

### 1. Creating Wallets

Generate new wallets using the `create_wallet.py` script:

```bash
# Create a single wallet
python create_wallet.py

# Create multiple wallets
python create_wallet.py --count 5

# Generate a sample wallet card
python create_wallet.py --sample
```

This will create:
- Individual JSON files for each wallet
- A combined JSON file with all wallets
- A PDF file with printable wallet cards
- A list of public addresses for distribution

### 2. Distributing POL

Use `distribute_pol.py` to send POL to multiple wallets:

```bash
# Test mode (simulates transactions without sending)
python distribute_pol.py --test --amount 0.1

# Real transaction
python distribute_pol.py --amount 0.1
```

Required parameters:
- `--amount`: Amount of POL to send to each wallet (must be greater than 0)

Optional parameters:
- `--test`: Run in test mode (simulates transactions without sending)

### Output Files

The scripts generate several files:

- `wallet_TIMESTAMP_N.json`: Individual wallet files
- `all_wallets_TIMESTAMP.json`: Combined wallet information
- `wallet_cards_TIMESTAMP.pdf`: Printable wallet cards
- `pol_distribution_log_TIMESTAMP.txt`: Transaction logs

## Security Considerations

1. Never share your private keys or mnemonic phrases
2. Keep wallet information secure and backed up
3. Always test transactions with small amounts first
4. Store wallet backups in a secure, offline location
5. Verify all transaction details before sending

## Error Handling

The script includes comprehensive error handling for:
- Invalid amounts (zero or negative)
- Insufficient balance
- Network connectivity issues
- Missing or invalid wallet files
- Invalid private keys

## File Structure

```
.
├── README.md
├── requirements.txt
├── distribute_pol.py      # Main distribution script
├── create_wallet.py       # Wallet creation script
├── test_pol_contract.py  # Contract testing utilities
└── privatekey.txt        # Sender's private key (not included in repo)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is provided "as is" without warranty of any kind. Use at your own risk. Always verify transactions and amounts before sending real funds. 