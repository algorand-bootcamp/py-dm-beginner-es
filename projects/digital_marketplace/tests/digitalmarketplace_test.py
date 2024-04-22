import algokit_utils
import algosdk
import pytest
from algokit_utils.beta.account_manager import AddressAndSigner
from algokit_utils.beta.algorand_client import (
    AlgorandClient,
    AssetCreateParams,
    AssetOptInParams,
    AssetTransferParams,
    PayParams,
)
from algosdk.atomic_transaction_composer import TransactionWithSigner

from smart_contracts.artifacts.digitalmarketplace.client import DigitalmarketplaceClient


@pytest.fixture(scope="session")
def algorand() -> AlgorandClient:
    """Genera un cliente de Algorand para interactuar con la app"""
    return AlgorandClient.default_local_net()


@pytest.fixture(scope="session")
def dispenser(algorand: AlgorandClient) -> AddressAndSigner:
    return algorand.account.dispenser()


@pytest.fixture(scope="session")
def creator(algorand: AlgorandClient, dispenser: AddressAndSigner) -> AddressAndSigner:
    acct = algorand.account.random()

    algorand.send.payment(
        PayParams(sender=dispenser.address, receiver=acct.address, amount=10_000_000)
    )

    return acct


@pytest.fixture(scope="session")
def test_asset_id(algorand: AlgorandClient, creator: AddressAndSigner) -> int:
    sent_txn = algorand.send.asset_create(
        AssetCreateParams(sender=creator.address, total=10)
    )
    return sent_txn["confirmation"]["asset-index"]


@pytest.fixture(scope="session")
def digital_marketplace_client(
    algorand: AlgorandClient, creator: AddressAndSigner, test_asset_id: int
) -> DigitalmarketplaceClient:
    client = DigitalmarketplaceClient(
        algod_client=algorand.client.algod,
        sender=creator.address,
        signer=creator.signer,
    )

    client.create_create_application(asset_id=test_asset_id, unitary_price=0)

    return client


def test_opt_in_to_asset(
    algorand: AlgorandClient,
    digital_marketplace_client: DigitalmarketplaceClient,
    test_asset_id: int,
    creator: AddressAndSigner,
):
    # Revisar que no haya un optin previo
    pytest.raises(
        algosdk.error.AlgodHTTPError,
        lambda: algorand.account.get_asset_information(
            digital_marketplace_client.app_address, test_asset_id
        ),
    )

    mbr_pay_txn = algorand.transactions.payment(
        PayParams(
            sender=creator.address,
            receiver=digital_marketplace_client.app_address,
            amount=200_000,
        )
    )

    sp = algorand.client.algod.suggested_params()
    sp.fee = 1000
    result = digital_marketplace_client.opt_in_to_asset(
        mbr_pay=TransactionWithSigner(txn=mbr_pay_txn, signer=creator.signer),
        transaction_parameters=algokit_utils.TransactionParameters(
            foreign_assets=[test_asset_id], suggested_params=sp
        ),
    )
    assert result.confirmed_round

    assert (
        algorand.account.get_asset_information(
            digital_marketplace_client.app_address, test_asset_id
        )["asset-holding"]["amount"]
        == 0
    )


def test_deposit(
    algorand: AlgorandClient,
    digital_marketplace_client: DigitalmarketplaceClient,
    test_asset_id: int,
    creator: AddressAndSigner,
):
    result = algorand.send.asset_transfer(
        AssetTransferParams(
            sender=creator.address,
            receiver=digital_marketplace_client.app_address,
            asset_id=test_asset_id,
            amount=5,
        )
    )

    assert result["confirmation"]

    assert (
        algorand.account.get_asset_information(
            digital_marketplace_client.app_address, test_asset_id
        )["asset-holding"]["amount"]
        == 5
    )


def test_set_price(digital_marketplace_client: DigitalmarketplaceClient):
    result = digital_marketplace_client.set_price(unitary_price=300_000)
    assert result.confirmed_round


def test_buy(
    algorand: AlgorandClient,
    digital_marketplace_client: DigitalmarketplaceClient,
    test_asset_id: int,
    creator: AddressAndSigner,
    dispenser: AddressAndSigner,
):
    buyer = algorand.account.random()

    algorand.send.payment(
        PayParams(sender=dispenser.address, receiver=buyer.address, amount=10_000_000)
    )

    algorand.send.asset_opt_in(
        AssetOptInParams(sender=buyer.address, asset_id=test_asset_id)
    )

    buyer_txn = algorand.transactions.payment(
        PayParams(
            sender=buyer.address,
            receiver=digital_marketplace_client.app_address,
            amount=3 * 300_000,
            extra_fee=1000,
        )
    )

    result = digital_marketplace_client.buy(
        quantity=3,
        buyer_txn=TransactionWithSigner(txn=buyer_txn, signer=buyer.signer),
        transaction_parameters=algokit_utils.TransactionParameters(
            foreign_assets=[test_asset_id],
            sender=buyer.address,
            signer=buyer.signer,
        ),
    )

    assert result.confirmed_round

    assert (
        algorand.account.get_asset_information(buyer.address, test_asset_id)[
            "asset-holding"
        ]["amount"]
        == 3
    )


def test_delete_application(
    algorand: AlgorandClient,
    digital_marketplace_client: DigitalmarketplaceClient,
    test_asset_id: int,
    creator: AddressAndSigner,
    dispenser: AddressAndSigner,
):
    before_call_amount = algorand.account.get_information(creator.address)["amount"]

    result = digital_marketplace_client.delete_delete_application(
        transaction_parameters=algokit_utils.TransactionParameters(
            foreign_assets=[test_asset_id],
        )
    )

    assert result.confirmed_round

    after_call_amount = algorand.account.get_information(creator.address)["amount"]

    assert after_call_amount == before_call_amount + 3 * 300_000 + 200_000 - 3000

    assert (
        algorand.account.get_asset_information(creator.address, test_asset_id)[
            "asset-holding"
        ]["amount"]
        == 7
    )
