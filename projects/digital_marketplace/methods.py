import algokit_utils
from algokit_utils.beta.algorand_client import AlgorandClient, AssetCreateParams, AssetTransferParams, PayParams

from smart_contracts.artifacts.digitalmarketplace.client import DigitalmarketplaceClient

# algorand = AlgorandClient.default_local_net()
# creator = algorand.account.random()
# dispenser = algorand.account.dispenser()
# algorand.send.payment(
#     PayParams(sender=dispenser.address, receiver=creator.address, amount=10_000_000)
# )
# dm_client = DigitalmarketplaceClient(
#         algod_client=algorand.client.algod,
#         sender=creator.address,
#         signer=creator.signer,
#     )

# create_result = dm_client.create_create_application(asset_id=0, unitary_price=0)
# print(create_result.tx_info


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
            receiver=create_result.tx_info["application-address"],
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
            receiver=create_result.tx_info["application-address"],
            asset_id=asset_id,
            amount=quantity
        )
    )

    set_app_id(create_result.tx_info["application-index"])

def buy(
    algorand: AlgorandClient,
    dm_client: DigitalmarketplaceClient,
    sender: str,
    app_address: str,
    quantity: int,
    unitary_price: int,
    set_units_left: callable,
) -> None:
    buyer_txn = algorand.transactions.payment(
        PayParams(
            sender=sender,
            receiver=app_address,
            amount=quantity*unitary_price,
            extra_fee=1_000
        )
    )

    state = dm_client.get_global_state()

    dm_client.buy(
       quantity=quantity,
       buyer_txn=buyer_txn,
         transaction_parameters=algokit_utils.TransactionParameters(
              foreign_assets=[state["asset_id"]]
         )
    )

    set_units_left(algorand.account.get_asset_information(app_address, state["asset_id"])["asset-holding"]["amount"])

def delete_application(
    dm_client: DigitalmarketplaceClient,
    set_app_id: callable
) -> None:
   dm_client.delete_delete_application(transaction_parameters=algokit_utils.TransactionParameters(
        foreign_assets=[dm_client.get_global_state()["asset_id"]],
    ))
   set_app_id(0)
