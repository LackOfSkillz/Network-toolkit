import React, {useState} from 'react'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'

export default function App(){
  const [view, setView] = useState(localStorage.getItem('authToken') ? 'dashboard' : 'login')

  function onLogin(){
    setView('dashboard')
  }

  function logout(){
    localStorage.removeItem('authToken')
    setView('login')
  }

  return (
    <div>
      <header style={{padding:12, borderBottom:'1px solid #eee'}}>
        <strong>Network Toolkit</strong>
        {view === 'dashboard' && <button style={{float:'right'}} onClick={logout}>Logout</button>}
      </header>
      {view === 'login' ? <LoginPage onLogin={onLogin}/> : <DashboardPage />}
    </div>
  )
}
