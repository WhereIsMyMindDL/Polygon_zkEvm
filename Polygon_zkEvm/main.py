from web3 import Web3
import json
import random
from tqdm import trange
import time
from loguru import logger
from sys import stderr
import telebot
from colorama import Fore



# ===================================== options ===================================== #

#----main-options----#
delay_wallets = [550, 650]                                          # минимальная и максимальная задержка между кошельками
delay_transactions = [20, 40]                                       # минимальная и максимальная задержка между транзакциями
value_eth = [0.00005, 0.00012]                                      # минимальное и максимальное кол-во eth для supply_ether_0vix, wrap_ether
try_again = 1                                                       # кол-во попыток в случае возникновения ошибок
shuffle = True                                                      # True / False если нужно перемешать кошельки
waiting_gas = 35                                                    # максимальный газ в сети эфир, при котором скрипт будет работать
decimal_places = 8                                                  # количество знаков, после запятой для генерации случайных чисел
rpc = 'https://polygon-zkevm.rpc.thirdweb.com'                      # rpc ноды
use_proxies = True                                                  # True / False. Если True, тогда будет использовать прокси (прокси = приватники)

#----modules-options----#
supply_ether_0vix = True                                            # True / False
borrow_0vix_random = True                                           # True / False
wrap_ether = True                                                   # True / False
bungee_refuelgas = True                                             # True / False
merkly_NFT_mint_and_bridge = True                                   # True / False

#------bot-options------#
bot_status = True                                                   # True / False
bot_token  = ''       						    # telegram bot token
bot_id     = 0                                              	    # telegram id

# =================================== end-options =================================== #


logger.remove()
logger.add(stderr, format="<lm>{time:YYYY-MM-DD HH:mm:ss}</lm> | <level>{level: <8}</level>| <lw>{message}</lw>")

number_wallets = 0
SUCCESS = '✅ '
ERROR = '❌ '
FAILED = '⚠️ '
send_list = []


with open('wallets.txt', 'r') as file:     # privatekey в файл wallets.txt
	wallets = [row.strip() for row in file]
with open('proxies.txt', 'r') as file:     # login:password@ip:port в файл proxy.txt
	proxies = [row.strip() for row in file]

def sleeping_wallets(x):
    for i in trange(x, desc=f'{Fore.LIGHTBLACK_EX}sleep...', ncols=50, bar_format='{desc}  {n_fmt}/{total_fmt}s |{bar}| {percentage:3.0f}%'):
        time.sleep(1)

def sleeping_transactions(x):
    for i in trange(x, desc=f'{Fore.LIGHTBLACK_EX}sleep between transaction...', ncols=65, bar_format='{desc}  {n_fmt}/{total_fmt}s |{bar}| {percentage:3.0f}%'):
        time.sleep(1)
    print()

def send_message():
    try:
        str_send = '\n'.join(send_list)
        bot = telebot.TeleBot(bot_token)
        bot.send_message(bot_id, str_send, parse_mode='html')
    except Exception as error:
        logger.error(error)

def add_gas_limit(transaction):
    try:
        gasLimit = rpc_url.eth.estimate_gas(transaction)
        transaction['gas'] = int(gasLimit * random.uniform(1.1, 1.2))
    except:
        transaction['gas'] = random.randint(380000, 420000)
    return transaction

def wait_gas():
    rpc_url_eth = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
    gas = rpc_url_eth.to_wei(waiting_gas, 'gwei')
    while True:
        gasPrice = int(rpc_url_eth.eth.gas_price)
        if gasPrice < gas:
            break
        logger.info(f'Waiting {waiting_gas} Gwei. Actual: {round(rpc_url_eth.from_wei(gasPrice, "gwei"), 1)} Gwei')
        time.sleep(120)

def retry_function(function, retry):
    if retry < try_again:
        logger.info(f"try again in {10} sec.")
        sleeping_wallets(10)
        function(address, private_key, value, retry + 1)
    else:
        return None

def convert_to(number, base, upper=False):
    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    if base > len(digits): return None
    result = ''
    while number > 0:
        result = digits[number % base] + result
        number //= base
    return result.upper() if upper else result

def intro():
    print()
    print(f'Subscribe: https://t.me/CryptoMindYep')
    print(f'Total wallets: {len(wallets)}\n')
    input('Press ENTER: ')
    print()

    print(f'| {Fore.LIGHTGREEN_EX}Polygon_zkEvm{Fore.RESET} |'.center(100, '='))
    print('\n')

def outro():
    for i in trange(3, desc=f'{Fore.LIGHTBLACK_EX}End process...', ncols=50, bar_format='{desc} {percentage:3.0f}%'):
        time.sleep(1)
    print(f'{Fore.RESET}\n')
    print(f'| {Fore.LIGHTGREEN_EX}END{Fore.RESET} |'.center(100, '='))
    print()
    print(input(f'Если помог скрипт: https://t.me/CryptoMindYep\nMetamask: 0x5AfFeb5fcD283816ab4e926F380F9D0CBBA04d0e'))

def supply_eth_0vix(address, private_key, value, retry=0):
    try:

        contract_address = '0xee1727f5074e747716637e1776b7f7c7133f16b1'  # адресс контракта

        transaction = {
            'to': rpc_url.to_checksum_address(contract_address),
            'value': int(rpc_url.to_wei(value, 'ether')),
            'data': '0x1249c58b',
            'chainId': 1101,
            'nonce': rpc_url.eth.get_transaction_count(address),
            'gasPrice': int(rpc_url.eth.gas_price * random.uniform(1.09, 1.14)),
        }

        add_gas_limit(transaction)

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'0vix: Supply {"{:0.9f}".format(value)} eth check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status

        if txstatus == 1:
            logger.success(f'0vix: Supply {"{:0.9f}".format(value)} eth - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            send_list.append(f'\n{SUCCESS}0vix: Supply {"{:0.9f}".format(value)} eth - transaction success')

        else:
            logger.error(f'0vix: Supply {"{:0.9f}".format(value)} eth - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            send_list.append(f'\n{FAILED}0vix: Supply eth - transaction failed')
            retry_function(supply_eth_0vix, retry)
    except:
        logger.error(f'{address} - ERROR Supply eth')
        send_list.append(f'\n{ERROR}0vix: Supply eth - transaction failed')
        retry_function(supply_eth_0vix, retry)

def borrow_0vix(address, private_key, value, retry=0):
    try:

        data = {
            'USDT': ['0xad41c77d99e282267c1492cdefe528d7d5044253', '0xc5ebeaec000000000000000000000000000000000000000000000000000000000000', random.randint(10000, 20000)],
            'USDC': ['0x68d9baa40394da2e2c1ca05d30bf33f52823ee7b', '0xc5ebeaec000000000000000000000000000000000000000000000000000000000000', random.randint(10000, 20000)],
            'MATIC': ['0x8903dc1f4736d2fcb90c1497aebbaba133daac76', '0xc5ebeaec00000000000000000000000000000000000000000000000000', random.randint(10200000000000000, 70200000000000000)]
        }

        token = random.choice(list(data))

        borrow_value = data[token][2]

        transaction = {
            'to': rpc_url.to_checksum_address(data[token][0]),
            'value': 0,
            'data': f'{data[token][1]}{convert_to(borrow_value, 16)}',
            'chainId': 1101,
            'nonce': rpc_url.eth.get_transaction_count(address),
            'gasPrice': int(rpc_url.eth.gas_price * random.uniform(1.09, 1.11)),
        }

        add_gas_limit(transaction)

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        if token != 'MATIC':
            borrow_value /= 1000000
        else:
            borrow_value = rpc_url.from_wei(borrow_value, "ether")
        logger.info(f'Borrow {"{:0.9f}".format(borrow_value)} {token} check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status

        if txstatus == 1:
            logger.success(f'0vix: Borrow {"{:0.9f}".format(borrow_value)} {token} - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            send_list.append(f'\n{SUCCESS}0vix: Borrow {"{:0.11f}".format(borrow_value)} {token} - transaction success')

        else:
            logger.error(f'0vix: Borrow {"{:0.9f}".format(borrow_value)} {token} - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            send_list.append(f'\n{FAILED}0vix: Borrow {token} - transaction failed')
            retry_function(borrow_0vix, retry)
    except:
        logger.error(f'{address} - ERROR Borrow {token}')
        send_list.append(f'\n{ERROR}0vix: Borrow {token} - transaction failed')
        retry_function(borrow_0vix, retry)

def wrap_eth(address, private_key, value, retry=0):
    try:

        transaction = {
            'to': rpc_url.to_checksum_address('0x4f9a0e7fd2bf6067db6994cf12e4495df938e6e9'),
            'value': int(rpc_url.to_wei(value, 'ether')),
            'data': '0xd0e30db0',
            'chainId': 1101,
            'nonce': rpc_url.eth.get_transaction_count(address),
            'gasPrice': int(rpc_url.eth.gas_price * random.uniform(1.09, 1.14)),
        }

        add_gas_limit(transaction)

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Wrap: {"{:0.9f}".format(value)} eth check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status

        if txstatus == 1:
            logger.success(f'Wrap: {"{:0.9f}".format(value)} eth - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            send_list.append(f'\n{SUCCESS}Wrap: {"{:0.9f}".format(value)} eth to weth - transaction success')

        else:
            logger.error(f'Wrap: {"{:0.9f}".format(value)} eth - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            send_list.append(f'\n{FAILED}Wrap: {"{:0.9f}".format(value)} eth - transaction failed')
            retry_function(wrap_eth, retry)
    except:
        logger.error(f'{address} - ERROR Wrap eth')
        send_list.append(f'\n{ERROR}Wrap: {"{:0.9f}".format(value)} eth - transaction failed')
        retry_function(wrap_eth, retry)

def bungee_refuel(address, private_key, value, retry=0):
    data = {
        'BSC': [56, round(random.uniform(0.000350001, 0.000400001), decimal_places)],
        'Gnosis': [1313161554, round(random.uniform(0.000050001, 0.000100001), decimal_places)],
        'Aurora': [100, round(random.uniform(0.000050001, 0.000100001), decimal_places)],
    }

    to_network = random.choice(list(data))

    try:
        abi = json.loads('[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"destinationReceiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":true,"internalType":"uint256","name":"destinationChainId","type":"uint256"}],"name":"Deposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Donation","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"}],"name":"GrantSender","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"}],"name":"RevokeSender","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"receiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"bytes32","name":"srcChainTxHash","type":"bytes32"}],"name":"Send","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"receiver","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"Withdrawal","type":"event"},{"inputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"isEnabled","type":"bool"}],"internalType":"struct GasMovr.ChainData[]","name":"_routes","type":"tuple[]"}],"name":"addRoutes","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable[]","name":"receivers","type":"address[]"},{"internalType":"uint256[]","name":"amounts","type":"uint256[]"},{"internalType":"bytes32[]","name":"srcChainTxHashes","type":"bytes32[]"},{"internalType":"uint256","name":"perUserGasAmount","type":"uint256"},{"internalType":"uint256","name":"maxLimit","type":"uint256"}],"name":"batchSendNativeToken","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"chainConfig","outputs":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"isEnabled","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"destinationChainId","type":"uint256"},{"internalType":"address","name":"_to","type":"address"}],"name":"depositNativeToken","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"chainId","type":"uint256"}],"name":"getChainData","outputs":[{"components":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"isEnabled","type":"bool"}],"internalType":"struct GasMovr.ChainData","name":"","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"}],"name":"grantSenderRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"processedHashes","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"}],"name":"revokeSenderRole","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"receiver","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"bytes32","name":"srcChainTxHash","type":"bytes32"},{"internalType":"uint256","name":"perUserGasAmount","type":"uint256"},{"internalType":"uint256","name":"maxLimit","type":"uint256"}],"name":"sendNativeToken","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"senders","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"chainId","type":"uint256"},{"internalType":"bool","name":"_isEnabled","type":"bool"}],"name":"setIsEnabled","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"setPause","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"setUnPause","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"withdrawBalance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_to","type":"address"}],"name":"withdrawFullBalance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]')
        contract = rpc_url.eth.contract(address=rpc_url.to_checksum_address('0x555a64968e4803e27669d64e349ef3d18fca0895'), abi=abi)

        build_tx_data = {
            'gasPrice': int(rpc_url.eth.gas_price * random.uniform(1.09, 1.14)),
            'from': rpc_url.to_checksum_address(address.lower()),
            'nonce': rpc_url.eth.get_transaction_count(address),
            'value': int(rpc_url.to_wei(data[to_network][1], "ether")),
            'gas': 0
        }

        transaction = contract.functions.depositNativeToken(data[to_network][0], address).build_transaction(build_tx_data)
        add_gas_limit(transaction)

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Bungee: refuel {"{:0.9f}".format(data[to_network][1])} eth from zkEVM to {to_network} check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status

        if txstatus == 1:
            logger.success(f'Bungee: refuel {"{:0.9f}".format(data[to_network][1])} eth from zkEVM to {to_network} - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            send_list.append(f'\n{SUCCESS}Bungee: refuel {"{:0.9f}".format(data[to_network][1])} eth to {to_network} - transaction success')

        else:
            logger.error(f'Bungee: refuel - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            send_list.append(f'\n{FAILED}Bungee: refuel - transaction failed')
            retry_function(bungee_refuel, retry)

    except:
        logger.error(f'ERROR Bungee refuel - {address}')
        send_list.append(f'\n{ERROR}Bungee: refuel - transaction failed')
        retry_function(bungee_refuel, retry)

def merkly_NFT(address, private_key, value, retry=0):
    try:
        transaction = {
            'to': rpc_url.to_checksum_address('0xb58f5110855fbef7a715d325d60543e7d4c18143'),
            'value': int(rpc_url.to_wei(0.0004, 'ether')),
            'data': '0x1249c58b',
            'chainId': 1101,
            'nonce': rpc_url.eth.get_transaction_count(address),
            'gasPrice': int(rpc_url.eth.gas_price * random.uniform(1.09, 1.14)),
        }

        add_gas_limit(transaction)

        signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f'Mint Merkly NFT check status tx - {rpc_url.to_hex(tx_hash)}')
        txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status
        if txstatus == 1:
            logger.success(f'Merkly: Mint NFT - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            result = rpc_url.eth.get_transaction_receipt(rpc_url.to_hex(tx_hash))
            data = json.loads(rpc_url.to_json(result))
            tokenId = data['logs'][0]['topics'][3][-6:]
            try:
                sleeping_transactions(random.randint(delay_transactions[0], delay_transactions[1]))
                transaction = {
                    'to': rpc_url.to_checksum_address('0xb58f5110855fbef7a715d325d60543e7d4c18143'),
                    'data': f'0x51905636000000000000000000000000{address[2:]}000000000000000000000000000000000000000000000000000000000000006a00000000000000000000000000000000000000000000000000000000000000e00000000000000000000000000000000000000000000000000000000000{tokenId}000000000000000000000000{address[2:]}000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001200000000000000000000000000000000000000000000000000000000000000014{address[2:]}000000000000000000000000000000000000000000000000000000000000000000000000000000000000002200010000000000000000000000000000000000000000000000000000000000061a80000000000000000000000000000000000000000000000000000000000000',
                    'chainId': 1101,
                    'gasPrice': int(rpc_url.eth.gas_price * random.uniform(1.09, 1.14)),
                    'nonce': rpc_url.eth.get_transaction_count(address),
                    'value': int(rpc_url.to_wei(0.00029996060493127, "ether")),
                }

                add_gas_limit(transaction)
                signed_txn = rpc_url.eth.account.sign_transaction(transaction, private_key)
                tx_hash = rpc_url.eth.send_raw_transaction(signed_txn.rawTransaction)
                logger.info(f'Merkly: Bridge NFT check status tx - {rpc_url.to_hex(tx_hash)}')
                txstatus = rpc_url.eth.wait_for_transaction_receipt(tx_hash).status
                if txstatus == 1:
                    logger.success(f'Merkly: Mint and Bridge NFT :  https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
                    send_list.append(f'\n{SUCCESS}Merkly: Mint and Bridge NFT - transaction success')
                else:
                    logger.error(f'Merkly: Bridge NFT :  https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
                    send_list.append(f'\n{FAILED}Merkly: Bridge NFT - transaction failed')
                    retry_function(merkly_NFT, retry)

            except:
                logger.error(f'ERROR bridge Merkly NFT - {address}')
                send_list.append(f'\n{ERROR}Merkly: Bridge NFT - transaction failed')
                retry_function(merkly_NFT, retry)

        else:
            logger.error(f'Merkly: Mint NFT - https://zkevm.polygonscan.com/tx/{rpc_url.to_hex(tx_hash)}')
            send_list.append(f'\n{FAILED}Merkly: Mint NFT - transaction failed')
            retry_function(merkly_NFT, retry)

    except:
        logger.error(f'{address} - ERROR Mint Merkly NFT')
        send_list.append(f'\n{ERROR}Merkly: Mint NFT - transaction failed')
        retry_function(merkly_NFT, retry)

def sb0vix(address, private_key, value):
    supply_eth_0vix(address, private_key, value, retry=0)
    if borrow_0vix_random == True:
        sleeping_transactions(random.randint(delay_transactions[0], delay_transactions[1]))
        borrow_0vix(address, private_key, value, retry=0)

def check_rpc(rpc_url, retry = 1):
    if rpc_url.is_connected() == True:
        return rpc_url.is_connected()
    else:
        logger.error(f'error connect to rpc... sleep 10 sec')
        time.sleep(10)
        if retry == 2:
            logger.error(f'failed')
            return rpc_url.is_connected()
        check_rpc(rpc_url, retry+1)

if __name__ == '__main__':
    intro()
    rpc_url = Web3(Web3.HTTPProvider(rpc))
    count_wallets = len(wallets)
    number_wallets = 0
    activities_list = []
    proxy_list = []
    for i in proxies:
        proxy_list.append(i)
    if supply_ether_0vix == True:
        activities_list.append(sb0vix)
    if wrap_ether == True:
        activities_list.append(wrap_eth)
    if merkly_NFT_mint_and_bridge == True:
        activities_list.append(merkly_NFT)
    if bungee_refuelgas == True:
        activities_list.append(bungee_refuel)


    if shuffle:
        random.shuffle(wallets)

    def start():
        global number_wallets, address, private_key, value
        while wallets:
            if use_proxies == True:
                try:
                    proxy = proxy_list[number_wallets]
                    rpc_url = Web3(Web3.HTTPProvider(rpc, request_kwargs={"proxies": {'https': "http://" + proxy, 'http': "http://" + proxy}}))
                except:
                    rpc_url = Web3(Web3.HTTPProvider(rpc))
            else:
                rpc_url = Web3(Web3.HTTPProvider(rpc))

            send_list.clear()
            number_wallets += 1
            private_key = wallets.pop(0)
            account = rpc_url.eth.account.from_key(private_key)
            address = account.address

            print(f'{number_wallets}/{count_wallets} - {address}\n')
            send_list.append(f'{number_wallets}/{count_wallets} : {address}')

            random.shuffle(activities_list)

            wait_gas()

            for i in range(len(activities_list)):
                value = round(random.uniform(value_eth[0], value_eth[1]), decimal_places)
                activities_list[i](address, private_key, value)
                if i != len(activities_list)-1:
                    sleeping_transactions(random.randint(delay_transactions[0], delay_transactions[1]))

            if bot_status == True:
                if number_wallets == count_wallets:
                    send_list.append(f'\nSubscribe: https://t.me/CryptoMindYep')
                send_message()
            if number_wallets != count_wallets:
                sleeping_wallets(random.randint(delay_wallets[0], delay_wallets[1]))
                print()


    start()
outro()
