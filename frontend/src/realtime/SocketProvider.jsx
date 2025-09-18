import React, { createContext, useContext, useEffect, useRef, useState } from 'react'
import { io } from 'socket.io-client'

const SocketContext = createContext(null)

export function SocketProvider({ children }){
  const [connected, setConnected] = useState(false)
  const socketRef = useRef(null)

  useEffect(()=>{
    // connect to backend socket.io endpoint
    try{
      const socket = io('/', { path: '/socket.io' })
      socketRef.current = socket
      socket.on('connect', () => setConnected(true))
      socket.on('disconnect', () => setConnected(false))

      return () => {
        try{ socket.disconnect() }catch(e){}
      }
    }catch(e){
      // graceful fallback: nothing to do if client lib can't connect
    }
  }, [])

  return (
    <SocketContext.Provider value={{ socket: socketRef.current, connected }}>
      {children}
    </SocketContext.Provider>
  )
}

export function useSocketContext(){
  return useContext(SocketContext)
}

export default SocketProvider
