from web3 import Web3
import json
import time
import threading

# Kết nối đến mạng Base
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# Địa chỉ hợp đồng và ABI của nó
contract_address = '0xE28c1a85268B081CbaeA8B71e3464E132aA8a0d4'
with open('abi.json', 'r') as f:
    abi = json.load(f)
contract = w3.eth.contract(address=contract_address, abi=abi)

# Đọc danh sách ví và private key từ tệp (đảm bảo bảo mật tệp này!)
with open('wallets_with_keys.txt', 'r') as f:  
    wallet_data = [line.strip().split(',') for line in f]  


def claim_airdrop(account):
    try:
        # Kiểm tra xem đã claim chưa
        has_claimed = contract.functions.claimed(account.address).call()
        if has_claimed:
            print(f'Already claimed for {account.address}')
            return

        # Nếu chưa claim, thực hiện claim
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price
        tx = contract.functions.claim().buildTransaction({
            'chainId': 8453,
            'gas': 300000,  
            'gasPrice': gas_price,
            'nonce': nonce,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f'Claimed successfully for {account.address} - Transaction hash: {tx_hash.hex()}')
    except Exception as e:
        print(f'Error claiming for {account.address}: {e}')

# Sử dụng đa luồng để tăng tốc
threads = []
for wallet_address, private_key in wallet_data:
    account = w3.eth.account.from_key(private_key)
    t = threading.Thread(target=claim_airdrop, args=(account,))
    threads.append(t)
    t.start()
    time.sleep(0.5)  

# Đợi tất cả các luồng hoàn thành
for t in threads:
    t.join()
