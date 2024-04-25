// src/components/Home.tsx
import * as algokit from '@algorandfoundation/algokit-utils'
import algosdk from "algosdk"
import { useWallet } from '@txnlab/use-wallet'
import React, { useEffect, useState } from 'react'
import ConnectWallet from './components/ConnectWallet'
import Transact from './components/Transact'
import { DigitalmarketplaceClient } from './contracts/Digitalmarketplace'
import { getAlgodConfigFromViteEnvironment } from './utils/network/getAlgoClientConfigs'
import MethodCall from './components/methodCall'
import * as methods from './methods'

interface HomeProps {}

const Home: React.FC<HomeProps> = () => {
  algokit.Config.configure({ populateAppCallResources: true})
  const [openWalletModal, setOpenWalletModal] = useState<boolean>(false)
  const [appId, setAppId]  = useState<number>(0)
  const [assetId, setAssetId] = useState<bigint>(0n)
  const [unitaryPrice, setUnitaryPrice] = useState<bigint>(0n)
  const [quantity, setQuantity] = useState<bigint>(0n)
  const [unitsLeft, setUnitsLeft] = useState<bigint>(0n)
  const { activeAddress, signer } = useWallet()

  useEffect(() => {
    dmClient.getGlobalState().then((globalState) => {
      setUnitaryPrice(globalState.unitaryPrice?.asBigInt() || 0n)
      const id = globalState.assetId?.asBigInt() || 0n
      setAssetId(id)
      algorand.account.getAssetInformation(algosdk.getApplicationAddress(appId), id).then((info) => {
        setUnitsLeft(info.balance)
      })
    }).catch(() => {
      setUnitaryPrice(0n)
      setAssetId(0n)
    })
  }, [appId])

  const toggleWalletModal = () => {
    setOpenWalletModal(!openWalletModal)
  }

  const algodConfig = getAlgodConfigFromViteEnvironment()
  const algorand = algokit.AlgorandClient.fromConfig({algodConfig})
  algorand.setDefaultSigner(signer)

  const dmClient = new DigitalmarketplaceClient({
      resolveBy: 'id',
      id: appId,
      sender: { addr: activeAddress!, signer },
  }, algorand.client.algod)


  return (
    <div className="hero min-h-screen bg-teal-400">
      <div className="hero-content text-center rounded-lg p-6 max-w-md bg-white mx-auto">
        <div className="max-w-md">
          <h1 className="text-4xl">
            Welcome to <div className="font-bold">AlgoKit 🙂</div>
          </h1>
          <p className="py-6">
            This starter has been generated using official AlgoKit React template. Refer to the resource below for next steps.
          </p>

          <div className="grid">
            <button data-test-id="connect-wallet" className="btn m-2" onClick={toggleWalletModal}>
              Wallet Connection
            </button>
            <div className="divider" />

            <label className="label">App ID: </label>
            <input type="number" className="input input-bordered" value={appId} min={0} onChange={(e) => setAppId(e.currentTarget.valueAsNumber)}/>
            <div className="divider" />
            { activeAddress && appId === 0 && (
              <div>
                <label className="label">Inserte Precio Unitario</label>
                <input type="number" className="input input-bordered" value={(unitaryPrice / BigInt(10e6)).toString()} onChange={(e) => {setUnitaryPrice(BigInt(e.currentTarget.valueAsNumber || 0) * BigInt(10e6))}}/>

                <label className="label">Cantidad de Assets</label>
                <input type="number" className="input input-bordered" value={quantity.toString()} onChange={(e) => {setQuantity(BigInt(e.currentTarget.valueAsNumber))}}/>

                <MethodCall methodFunction={methods.create(algorand, dmClient, activeAddress!, unitaryPrice, quantity, assetId, setAppId)} text={'Create App'} />
              </div>
            )}

            { appId && (
              <div>
                <label className="label">Asset ID</label>
                <input type="number" className="input input-bordered" value={assetId.toString()} readOnly={true} />

                <label className="label">Precio por Asset</label>
                <input type="number" className="input input-bordered" value={(unitaryPrice / BigInt(10e6)).toString()} readOnly={true} />

                <label className="label">Assets disponibles</label>
                <input type="number" className="input input-bordered" value={unitsLeft.toString()} readOnly={true} />
              </div>
            ) }
            <div className="divider" />
            { activeAddress && appId !== 0 && unitsLeft > 0n && (
              <div>


                <label className="label">Cuantos Assets desea comprar</label>
                <input type="number" className="input input-bordered" value={quantity.toString()} onChange={(e) => {setQuantity(BigInt(e.currentTarget.valueAsNumber))}} max={unitsLeft.toString()} min={0}/>


                <MethodCall methodFunction={methods.buy(algorand, dmClient, activeAddress!, algosdk.getApplicationAddress(appId), quantity, unitaryPrice, setUnitsLeft)} text ={`Comprar ${quantity} assets por ${unitaryPrice * BigInt(quantity) / BigInt(10e6)} ALGOs`}/>
              </div>
            )}

            { appId !== 0 && unitsLeft === 0n && (
              <button className="btn btn-disabled m-2">NO HAY ASSETS DISPONIBLES</button>

            )}


          </div>

          <ConnectWallet openModal={openWalletModal} closeModal={toggleWalletModal} />

        </div>
      </div>
    </div>
  )
}

export default Home
