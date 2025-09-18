/**
 * SNMP Options Modal
 *
 * Form to configure SNMP options for a device (credential selection,
 * enable/disable). For the demo it is a simple modal; comments here are
 * non-functional.
 */
import React, { useState } from 'react'
import CredentialSelect from '../EndpointConfig/CredentialSelect'

export default function SNMPOptionsModal({ device, open, onClose, onCollect }){
  const [credentialId, setCredentialId] = useState(null)
  const [enable, setEnable] = useState(Boolean(device?.enable_lldp))
  const [loading, setLoading] = useState(false)

  if(!open) return null

  async function toggleEnable(v){
    setEnable(v)
    // call backend toggle
    const token = localStorage.getItem('authToken')
    const headers = token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }
    await fetch(`/lldp/devices/${device.id}/enable?enable=${v}`, { method: 'POST', headers })
  }

  async function doCollect(){
    setLoading(true)
    try{
      const token = localStorage.getItem('authToken')
      const headers = token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }
      const resp = await fetch(`/lldp/collect/${device.id}`, { method: 'POST', headers })
      const body = await resp.json()
      // fetch neighbors for this run
      const neighborsResp = await fetch(`/lldp/devices/${device.id}/neighbors?run=${body.collector_run_id}`, { headers })
      const neighbors = await neighborsResp.json()
      onCollect && onCollect(device, body, neighbors)
    }catch(e){
      console.error(e)
      alert('Collection failed: '+ String(e))
    } finally { setLoading(false) }
  }

  return (
    <div style={{ position: 'fixed', left: '20%', top: '20%', width: '60%', background: '#fff', border: '1px solid #ccc', padding: 16, zIndex: 2000 }}>
      <h3>SNMP Options for {device.name || device.id}</h3>
      <div style={{ marginBottom: 8 }}>
        <label>Credentials</label>
        <CredentialSelect value={credentialId} onChange={(v)=> setCredentialId(v)} />
      </div>
      <div style={{ marginBottom: 8 }}>
        <label><input type="checkbox" checked={enable} onChange={(e)=> toggleEnable(e.target.checked)} /> Enable LLDP collection</label>
      </div>
      <div style={{ marginTop: 12 }}>
        <button onClick={doCollect} disabled={loading} className="btn">{loading ? 'Collecting...' : 'Collect LLDP/CDP'}</button>
        <button onClick={onClose} style={{ marginLeft: 8 }} className="btn">Close</button>
      </div>
    </div>
  )
}
