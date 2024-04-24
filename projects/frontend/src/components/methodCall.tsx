import { buffer } from "stream/consumers"

interface MethodCallInterface {
  methodFunction: () => Promise<void>
}

const MethodCall = ({ methodFunction }: MethodCallInterface) => {
  return
}
export default MethodCall
