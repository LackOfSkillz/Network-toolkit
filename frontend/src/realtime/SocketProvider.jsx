import React, { createContext, useContext, useEffect, useRef, useState } from 'react'
import { io } from 'socket.io-client'

const SocketContext = createContext(null)

export function SocketProvider({ children }){
  const [connected, setConnected] = useState(false)
  const socketRef = useRef(null)
  const tokenRef = useRef(null)

  // helper to (re)connect with the provided token
  function connectWithToken(token){
    try{
      // disconnect existing socket first
      if(socketRef.current){
        try{ socketRef.current.disconnect() }catch(e){}
        socketRef.current = null
      }

      const opts = { path: '/socket.io', auth: {} }
      if(token) opts.auth = { token }
      const socket = io('/', opts)
      socketRef.current = socket
      socket.on('connect', () => setConnected(true))
      socket.on('disconnect', () => setConnected(false))
      // forward any connection errors silently
      socket.on('connect_error', () => {})
    }catch(e){
      // graceful fallback
    }
  }

  useEffect(()=>{
    // initial connect using token from localStorage
    const initialToken = localStorage.getItem('authToken')
    tokenRef.current = initialToken
    connectWithToken(initialToken)

    // listen for token changes (other tabs) and reconnect
    function handleStorage(e){
      if(e.key === 'authToken'){
        const newToken = e.newValue
        if(newToken !== tokenRef.current){
          tokenRef.current = newToken
          connectWithToken(newToken)
        }
      }
    }
    window.addEventListener('storage', handleStorage)

    return ()=>{
      window.removeEventListener('storage', handleStorage)
      try{ if(socketRef.current) socketRef.current.disconnect() }catch(e){}
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
