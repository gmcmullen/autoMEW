from web3 import Web3
import json
from datetime import datetime
import os
import argparse
from mnemonic import Mnemonic
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import segno
from io import BytesIO

def create_qr_code(data):
    """Generate a QR code from the provided data and return it as PNG bytes."""
    qr = segno.make(data)
    buffer = BytesIO()
    qr.save(buffer, kind='png', scale=3)
    return buffer.getvalue()

def create_wallet_card(pdf, wallet_data):
    """Create a printable wallet card with QR code and wallet details."""
    # Add new page if current page is nearly full
    if pdf.get_y() > 250:
        pdf.add_page()
    
    start_y = pdf.get_y()
    
    # Generate QR code for private key (without '0x' prefix for MetaMask compatibility)
    private_key = wallet_data['private_key'].replace('0x', '')
    qr_code = create_qr_code(private_key)
    pdf.image(qr_code, x=10, y=start_y, w=35)
    
    # Position text to the right of QR code
    text_x = 55
    pdf.set_xy(text_x, start_y)
    
    # Add wallet details with consistent formatting
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 6, "Public Key:", new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.set_font("courier", "", 8)
    pdf.set_x(text_x)
    pdf.multi_cell(140, 4, wallet_data['public_key'])
    pdf.ln(1)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_x(text_x)
    pdf.cell(0, 6, "Private Key:", new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.set_font("courier", "", 8)
    pdf.set_x(text_x)
    pdf.multi_cell(140, 4, wallet_data['private_key'])
    pdf.ln(1)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_x(text_x)
    pdf.cell(0, 6, "Recovery Phrase:", new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.set_font("helvetica", "", 9)
    pdf.set_x(text_x)
    pdf.cell(0, 6, wallet_data['mnemonic'], new_x=XPos.LEFT, new_y=YPos.NEXT)
    
    # Add separator line between cards
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

def generate_sample_card():
    """Generate a sample wallet card for preview purposes."""
    sample_data = {
        "wallet_number": 1,
        "public_key": "0x1234567890abcdef1234567890abcdef12345678",
        "private_key": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        "mnemonic": "abandon ability able about above absent absorb abstract absurd abuse access accident",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    pdf = FPDF()
    pdf.add_page()
    create_wallet_card(pdf, sample_data)
    pdf.output("sample_wallet_card.pdf")
    print("\nSample wallet card has been generated as 'sample_wallet_card.pdf'")
    print("This shows how a single card will look when printed.")

def generate_wallet(wallet_number=None):
    """Generate a new Ethereum wallet with mnemonic phrase."""
    mnemo = Mnemonic("english")
    mnemonic = mnemo.generate(strength=128)  # Generate 12-word mnemonic
    
    # Create wallet from mnemonic
    w3 = Web3()
    seed = mnemo.to_seed(mnemonic)
    account = w3.eth.account.from_key(seed[:32])
    
    wallet_data = {
        "wallet_number": wallet_number if wallet_number else 1,
        "public_key": account.address,
        "private_key": account.key.hex(),
        "mnemonic": mnemonic,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Save wallet data to JSON file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"wallet_{timestamp}_{wallet_number}.json" if wallet_number else f"wallet_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(wallet_data, f, indent=4)
    
    return wallet_data, filename

def generate_multiple_wallets(count):
    """Generate multiple Ethereum wallets and create printable cards."""
    print(f"\nGenerating {count} wallets...\n")
    print("-" * 80)
    
    # Initialize PDF document
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    pdf_filename = f"wallet_cards_{timestamp}.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=10)
    
    all_wallets = []
    public_addresses = []
    
    for i in range(1, count + 1):
        wallet_data, filename = generate_wallet(i)
        all_wallets.append(wallet_data)
        public_addresses.append(wallet_data['public_key'])
        
        create_wallet_card(pdf, wallet_data)
        
        # Add new page after every 5 wallets
        if i % 5 == 0 and i < count:
            pdf.add_page()
        
        print(f"Wallet #{i}")
        print(f"Public Key: {wallet_data['public_key']}")
        print(f"Private Key: {wallet_data['private_key']}")
        print(f"Mnemonic Phrase: {wallet_data['mnemonic']}")
        print(f"Saved to: {filename}")
        print("-" * 80)
    
    # Save all generated files
    pdf.output(pdf_filename)
    
    master_filename = f"all_wallets_{timestamp}.json"
    with open(master_filename, 'w') as f:
        json.dump(all_wallets, f, indent=4)
    
    addresses_filename = f"public_addresses_{timestamp}.json"
    with open(addresses_filename, 'w') as f:
        json.dump({
            "addresses": public_addresses,
            "count": len(public_addresses),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }, f, indent=4)
    
    print(f"\nAll wallet information saved to: {master_filename}")
    print(f"Public addresses for token distribution saved to: {addresses_filename}")
    print(f"Printable wallet cards saved to: {pdf_filename}")
    print("\nIMPORTANT: Keep this information secure and never share your private keys or mnemonic phrases!")
    print("Consider storing these credentials offline for maximum security.")
    print("The mnemonic phrase can be used to recover your wallet - keep it safe!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Ethereum wallets')
    parser.add_argument('--count', type=int, default=1, help='Number of wallets to generate (default: 1)')
    parser.add_argument('--sample', action='store_true', help='Generate a sample wallet card')
    args = parser.parse_args()
    
    if args.sample:
        generate_sample_card()
    elif args.count < 1:
        print("Error: Number of wallets must be at least 1")
    else:
        if args.count == 1:
            wallet_data, filename = generate_wallet()
            
            # Generate single wallet card
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f"wallet_card_{timestamp}.pdf"
            pdf = FPDF()
            pdf.add_page()
            create_wallet_card(pdf, wallet_data)
            pdf.output(pdf_filename)
            
            print(f"\nWallet created successfully!")
            print(f"Public Key: {wallet_data['public_key']}")
            print(f"Private Key: {wallet_data['private_key']}")
            print(f"Mnemonic Phrase: {wallet_data['mnemonic']}")
            print(f"\nCredentials saved to: {filename}")
            print(f"Printable wallet card saved to: {pdf_filename}")
            print("\nIMPORTANT: Keep this information secure and never share your private key or mnemonic phrase!")
            print("The mnemonic phrase can be used to recover your wallet - keep it safe!")
        else:
            generate_multiple_wallets(args.count) 