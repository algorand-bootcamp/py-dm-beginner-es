import algokit_utils
from algokit_utils.beta.algorand_client import AlgorandClient, AssetCreateParams, AssetTransferParams, PayParams

from smart_contracts.artifacts.digitalmarketplace.client import DigitalmarketplaceClient


def create(
    algorand: AlgorandClient,
    dm_client: DigitalmarketplaceClient,
    sender: str,
    unitary_price: int,
    quantity: int,
    asset_being_sold: int,
    set_app_id: callable
) -> None:
  asset_id = asset_being_sold
  if (asset_id == 0):
    asset_create_result = algorand.send.asset_create(AssetCreateParams(
      sender=sender, 
      total=quantity
    ))
    asset_id = asset_create_result["confirmation"]["asset-index"]

    create_result = dm_client.create_create_application(asset_id=asset_id, unitary_price=unitary_price)

    mbr_txn = algorand.transactions.payment(
        PayParams(
            sender=sender,
            receiver=dm_client.app_address,
            amount=200_000,
            extra_fee=1_000
        )
    )

    dm_client.opt_in_to_asset(
        mbr_pay=mbr_txn,
        transaction_parameters=algokit_utils.TransactionParameters(
            foreign_assets=[asset_id]
        ),
    )

    algorand.send.asset_transfer(
        AssetTransferParams(
            sender=sender,
            receiver=dm_client.app_address,
            asset_id=asset_id,
            amount=quantity
        )
    )

    set_app_id(create_result.tx_info["application-index"])

def buy(
    algorand: AlgorandClient,
    dm_client: DigitalmarketplaceClient,
    sender: str,
    quantity: int,
    unitary_price: int,
    set_units_left: callable,
    asset_id: int,
) -> None:
    buyer_txn = algorand.transactions.payment(
        PayParams(
            sender=sender,
            receiver=dm_client.app_address,
            amount=quantity*unitary_price,
            extra_fee=1_000
        )
    )

    dm_client.buy(
       quantity=quantity,
       buyer_txn=buyer_txn,
         transaction_parameters=algokit_utils.TransactionParameters(
              foreign_apps=[asset_id]
         )
    )

    set_units_left(algorand.account.get_asset_information(dm_client.app_address, asset_id)["asset-holding"]["amount"])

def delete_application(
    dm_client: DigitalmarketplaceClient,
    asset_id: int,
    set_app_id: callable
) -> None:
   dm_client.delete_delete_application(transaction_parameters=algokit_utils.TransactionParameters(
        foreign_assets=[asset_id],
    ))
   set_app_id(0)
