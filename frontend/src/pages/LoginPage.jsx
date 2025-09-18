/**
 * LoginPage
 *
 * Presents a minimal login form. For the prototype the handler simply
 * calls `onLogin` with a token; in a real app this would POST to an
 * authentication endpoint.
 */
import React, {useState} from 'react'

export default function LoginPage({onLogin}){
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)

  async function submit(e){
    e.preventDefault()
    setError(null)
    try{
      const resp = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      })
      if(!resp.ok){
        const j = await resp.json().catch(()=>({detail:'login failed'}))
        setError(j.detail || 'Login failed')
        return
      }
      const j = await resp.json()
      const token = j.token
      if(token){
        localStorage.setItem('authToken', token)
        onLogin && onLogin()
      } else {
        setError('No token returned')
      }
    }catch(err){
      setError(err.message)
    }
  }

  return (
    <div style={{maxWidth:400, margin:'20px auto'}}>
      <h2>Login</h2>
      <form onSubmit={submit}>
        <div><label>Username<br/><input value={username} onChange={e=>setUsername(e.target.value)} /></label></div>
        <div><label>Password<br/><input type="password" value={password} onChange={e=>setPassword(e.target.value)} /></label></div>
        <div style={{marginTop:10}}>
          <button type="submit">Login</button>
        </div>
        {error && <div style={{color:'red', marginTop:10}}>{error}</div>}
      </form>
    </div>
  )
}
