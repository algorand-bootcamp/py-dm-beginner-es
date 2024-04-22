from algopy import ARC4Contract, Asset, Global, Txn, UInt64, arc4, gtxn, itxn


class Digitalmarketplace(ARC4Contract):
    asset_id: UInt64
    unitary_price: UInt64

    # Creación de la app
    @arc4.abimethod(allow_actions=["NoOp"], create="require")
    def create_application(self, asset_id: Asset, unitary_price: UInt64) -> None:
        self.asset_id = asset_id.id
        self.unitary_price = unitary_price

    # Hacer que el contrato haga opt in al asset
    @arc4.abimethod
    def opt_in_to_asset(self, mbr_pay: gtxn.PaymentTransaction) -> None:
        assert Txn.sender == Global.creator_address
        assert not Global.current_application_address.is_opted_in(Asset(self.asset_id))

        assert mbr_pay.receiver == Global.current_application_address
        assert mbr_pay.amount == Global.min_balance + Global.asset_opt_in_min_balance

        itxn.AssetTransfer(
            xfer_asset=self.asset_id,
            asset_receiver=Global.current_application_address,
            asset_amount=0,
        ).submit()

    # Usuario vendedor defina el precio de venta de lo assets
    @arc4.abimethod
    def set_price(self, unitary_price: UInt64) -> None:
        assert Txn.sender == Global.creator_address

        self.unitary_price = unitary_price

    # Usuario comprador puede hacer la compra de n assets
    @arc4.abimethod
    def buy(
        self,
        buyer_txn: gtxn.PaymentTransaction,
        quantity: UInt64,
    ) -> None:
        assert self.unitary_price != UInt64(0)

        assert buyer_txn.sender == Txn.sender
        assert buyer_txn.receiver == Global.current_application_address
        assert buyer_txn.amount == self.unitary_price * quantity

        itxn.AssetTransfer(
            xfer_asset=self.asset_id, asset_receiver=Txn.sender, asset_amount=quantity
        ).submit()

    # Usuario vendedor pueda reclamar las ganancias y assets sobrantes
    @arc4.abimethod(allow_actions=["DeleteApplication"])
    def delete_application(self) -> None:
        assert Txn.sender == Global.creator_address

        # Reclamar el saldo de los productos
        itxn.AssetTransfer(
            xfer_asset=self.asset_id,
            asset_receiver=Global.creator_address,
            asset_amount=0,
            asset_close_to=Global.creator_address,
        ).submit()

        # Reclamar las ganancias de algos
        itxn.Payment(
            receiver=Global.creator_address,
            amount=0,
            close_remainder_to=Global.creator_address,
        ).submit()
