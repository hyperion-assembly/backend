from decimal import Decimal
from thirdweb import ThirdwebSDK
from thirdweb.types import SDKOptions
from thirdweb.types.settings.metadata import TokenContractMetadata
from thirdweb.types.currency import TokenAmount
import logging
from django.conf import settings
from web3.datastructures import AttributeDict

logger = logging.getLogger(__name__)


class MissingThirdwebSecretKeyException(Exception):
    pass


class MissingTestPrivateKeyException(Exception):
    pass


def get_thirdweb_sdk():
    if not settings.THIRDWEB_API_KEY:
        raise MissingThirdwebSecretKeyException()

    if not settings.TEST_PRIVATE_KEY:
        raise MissingTestPrivateKeyException()

    return ThirdwebSDK.from_private_key(
        settings.TEST_PRIVATE_KEY, "goerli", SDKOptions(secret_key=settings.THIRDWEB_API_KEY)
    )


def create_token_contract(name: str, symbol: str, total_supply: Decimal, external_link: str | None):
    sdk = get_thirdweb_sdk()

    metadata = TokenContractMetadata(
        name=name,
        symbol=symbol,
        external_link=external_link,
        total_supply=total_supply,
    )
    onchain_address = sdk.deployer.deploy_token(metadata)
    return onchain_address


def mint_tokens(address: str, token_amounts: list[TokenAmount]) -> AttributeDict:
    logger.info(f"Start minting tokens for {address}")
    contract = get_thirdweb_sdk().get_token(address)

    if len(token_amounts) == 1:
        receipt = contract.mint_to(token_amounts[0].to_address, token_amounts[0].amount)
    else:
        receipt = contract.mint_batch_to(token_amounts)

    logger.info(f"Done minting tokens for {address}: receipt {receipt}")
    return receipt
