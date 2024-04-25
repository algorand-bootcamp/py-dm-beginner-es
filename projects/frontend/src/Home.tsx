// src/components/Home.tsx
import * as algokit from '@algorandfoundation/algokit-utils'
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
  const [quantity, setQuantity] = useState<bigint>(1n)
  const { activeAddress, signer } = useWallet()

  useEffect(() => {
    dmClient.getGlobalState().then((globalState) => {
      setUnitaryPrice(globalState.unitaryPrice?.asBigInt() || 0n)
      setAssetId(globalState.assetId?.asBigInt() || 0n)
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
            <input type="number" className="input input-bordered" value={appId} onChange={(e) => setAppId(e.currentTarget.valueAsNumber)}/>
            <div className="divider" />
            { activeAddress && appId === 0 && (
            <div>
                <MethodCall methodFunction={methods.create(algorand, dmClient, activeAddress!, unitaryPrice, quantity, assetId, setAppId)} text={'Create App'} />
            </div>
            )}

            { activeAddress && appId !== 0 && (
              <div>
                <label className="label">Price per Unit</label>
                <input type="text" className="input input-bordered" value={(unitaryPrice / BigInt(10e6)).toString()} readOnly={true}/>
              </div>
            )}


          </div>

          <ConnectWallet openModal={openWalletModal} closeModal={toggleWalletModal} />

        </div>
      </div>
    </div>
  )
}

export default Home
