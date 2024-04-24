// src/components/Home.tsx
import * as algokit from '@algorandfoundation/algokit-utils'
import { useWallet } from '@txnlab/use-wallet'
import React, { useState } from 'react'
import ConnectWallet from './components/ConnectWallet'
import Transact from './components/Transact'
import { DigitalmarketplaceClient } from './contracts/Digitalmarketplace'
import { getAlgodConfigFromViteEnvironment } from './utils/network/getAlgoClientConfigs'

interface HomeProps {}

const Home: React.FC<HomeProps> = () => {
  algokit.Config.configure({ populateAppCallResources: true})
  const [openWalletModal, setOpenWalletModal] = useState<boolean>(false)
  const { activeAddress } = useWallet()

  const toggleWalletModal = () => {
    setOpenWalletModal(!openWalletModal)
  }

  const algodConfig = getAlgodConfigFromViteEnvironment()
  const algorand = algokit.AlgorandClient.fromConfig({algodConfig})




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


          </div>

          <ConnectWallet openModal={openWalletModal} closeModal={toggleWalletModal} />

        </div>
      </div>
    </div>
  )
}

export default Home
