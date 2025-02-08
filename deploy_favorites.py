from vyper import compile_code
from web3 import Web3
from dotenv import load_dotenv
import os
import getpass
from eth_account import Account
from encrypt_key import KEYSTORE_PATH

load_dotenv()
RPC_URL=os.getenv("RPC_URL")
MY_ADDRESS=os.getenv("MY_ADDRESS")

def main():
    print("Compiling smart contract...\n")
    with open("favorites.vy", "r") as favorites_file:
        favorites_code = favorites_file.read()
        compilation_details = compile_code(favorites_code, output_formats = ["bytecode", "abi"])
        print(f"Compilation Details \n {compilation_details}")

        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        favorites_contract = w3.eth.contract(bytecode=compilation_details["bytecode"], abi=compilation_details["abi"])

        nonce = w3.eth.get_transaction_count(MY_ADDRESS)
        #manually creating transaction
        transaction = favorites_contract.constructor().build_transaction(
            {
                "nonce":nonce,
                "from": MY_ADDRESS,
                "gasPrice": w3.eth.gas_price
            }
        )

        private_key = decrypt_key()
        signed_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
        print(f"Signed Transaction \n {signed_transaction}")

        tx_hash = w3.eth.send_raw_transaction(signed_transaction.raw_transaction)
        print(f"Transaction hash \n {tx_hash}")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"The transaction has finished and the contract is deployed at {tx_receipt.contractAddress}")

def decrypt_key() -> str:
    with open(KEYSTORE_PATH, "r") as fp:
        encrypted_account = fp.read()
        password = getpass.getpass("Enter your password: ")
        key = Account.decrypt(encrypted_account, password)
        return key

if __name__ == "__main__":
    main()