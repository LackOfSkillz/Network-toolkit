import { useEffect } from 'react'
import { useSocketContext } from './SocketProvider'

export default function useSocket(event, handler){
  const ctx = useSocketContext()

  useEffect(()=>{
    const socket = ctx && ctx.socket
    if(!socket || !event || !handler) return

    socket.on(event, handler)
    return () => {
      try{ socket.off(event, handler) }catch(e){}
    }
  }, [ctx, event, handler])
}
