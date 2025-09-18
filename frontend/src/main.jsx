/**
 * main entry
 *
 * Bootstraps the React application and attaches it to the DOM. This file
 * composes the App with theme and socket providers. The comment here is
 * explanatory only.
 */
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import SocketProvider from './realtime/SocketProvider'
import ThemeProvider from './theme/themeProvider'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider>
      <SocketProvider>
        <App />
      </SocketProvider>
    </ThemeProvider>
  </React.StrictMode>
)
