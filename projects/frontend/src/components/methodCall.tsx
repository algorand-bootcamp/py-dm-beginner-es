import { useState } from "react"
import { buffer } from "stream/consumers"

interface MethodCallInterface {
  methodFunction: () => Promise<void>
  text: string
}

const MethodCall = ({ methodFunction, text }: MethodCallInterface) => {
  const [loading, setLoading] = useState<boolean>(false)
  const callMethodFunction = async() => {
    setLoading(true)
    await methodFunction()
    setLoading(false)
  }

  return <button className="btn m-2" onClick={callMethodFunction}>
    {loading ? <span className="loading loading-spinner"/> : text}
    </button>
}
export default MethodCall
