import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock socket.io-client module used by our SocketProvider — must be declared
// before importing the provider so the provider picks up the mock.
vi.mock('socket.io-client', () => {
  return {
    io: vi.fn((url, opts) => {
      // return a fake socket with minimal API
      const handlers = {}
      const socket = {
        connected: false,
        connect() { this.connected = true; if (handlers.connect) handlers.connect() },
        disconnect() { this.connected = false; if (handlers.disconnect) handlers.disconnect() },
        on(event, fn) { handlers[event] = fn },
        off(event) { delete handlers[event] },
        emit(event, ...args) { if (handlers[event]) handlers[event](...args) },
        // expose handlers for test to call
        __handlers: handlers,
      }
      // schedule a microtask so provider can register listeners first,
      // then simulate an immediate connect event
      Promise.resolve().then(() => {
        if (handlers.connect) handlers.connect()
      })
      return socket
    })
  }
})

import { SocketProvider, useSocketContext } from '../../../frontend/src/realtime/SocketProvider'
import { io } from 'socket.io-client'

function Consumer() {
  const ctx = useSocketContext()
  return React.createElement('div', null, ctx?.socket ? 'HAS_SOCKET' : 'NO_SOCKET')
}

describe('SocketProvider', ()=>{
  beforeEach(()=>{
    localStorage.clear()
  })

  afterEach(()=>{
    vi.clearAllMocks()
    localStorage.clear()
  })

  it('creates socket with token from localStorage', async ()=>{
    localStorage.setItem('authToken', 'tok-123')
    render(React.createElement(SocketProvider, null, React.createElement(Consumer)))
    expect(io).toHaveBeenCalled()
    const calledWith = io.mock.calls[0][1]
    expect(calledWith).toBeTruthy()
    expect(calledWith.auth).toEqual({ token: 'tok-123' })
    // wait for the mock to fire the connect handler and update context
    const el = await screen.findByText('HAS_SOCKET')
    expect(el).toBeTruthy()
  })

  it('reconnects when authToken changes via storage event', async ()=>{
    localStorage.setItem('authToken', 'a')
    render(React.createElement(SocketProvider, null, React.createElement(Consumer)))
    expect(io).toHaveBeenCalledTimes(1)
    // simulate token change in another tab by dispatching storage event
    localStorage.setItem('authToken', 'b')
    window.dispatchEvent(new StorageEvent('storage', { key: 'authToken', newValue: 'b' }))
    // wait for a reconnection attempt
    await (async function waitForCall(){
      for(let i=0;i<10;i++){
        if(io.mock.calls.length > 1) return
        await new Promise(r=>setTimeout(r, 20))
      }
      throw new Error('socket.io-client io was not called again')
    })()
    expect(io.mock.calls.length).toBeGreaterThan(1)
  })
})
