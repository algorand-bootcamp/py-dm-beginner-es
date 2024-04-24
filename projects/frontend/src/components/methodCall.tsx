import { buffer } from "stream/consumers"

interface MethodCallInterface {
  methodFunction: () => Promise<void>
  text: string
}

const MethodCall = ({ methodFunction, text }: MethodCallInterface) => {

  return <button className="btn m-2" onClick={methodFunction}>
    {text}
    </button>
}
export default MethodCall
