/**
 * App
 *
 * Top-level React application component that chooses between login and
 * dashboard pages. This header is purely descriptive.
 */
import React, {useState} from 'react'
import './styles/responsive.css'
import DashboardPage from './pages/DashboardPage'
import LoginPage from './pages/LoginPage'
import WelcomeTour from './components/WelcomeTour'

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
      {view === 'login' ? <LoginPage onLogin={onLogin}/> : (
        <div>
          {localStorage.getItem('seenWelcomeTour') ? null : <WelcomeTour onClose={()=>{}} />}
          <DashboardPage />
        </div>
      )}
    </div>
  )
}
