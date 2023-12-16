from ens.auto import ns
from django.conf import settings
from web3 import Web3

w3 = Web3(Web3.HTTPProvider(f"https://eth-mainnet.g.alchemy.com/v2/{settings.ALCHEMY_API_KEY}"))


def normalize_address(address):
    if address.endswith(".eth"):
        return w3.ens.address(address)
    else:
        return address
