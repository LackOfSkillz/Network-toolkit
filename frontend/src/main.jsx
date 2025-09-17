import React from "react"
import { createRoot } from "react-dom/client"
import DashboardPage from "./pages/DashboardPage"

function App(){
  return <DashboardPage />
}

createRoot(document.getElementById("root")).render(<App />)
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
