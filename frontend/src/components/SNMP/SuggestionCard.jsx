/**
 * SuggestionCard
 *
 * Small card used to present discovered LLDP neighbors and accept/reject
 * them into the topology. Documentation here is non-functional.
 */
import React from 'react'

export default function SuggestionCard({ neighbor, onAccept, onReject }){
  return (
    <div style={{ background: '#fff', border: '1px dashed #94a3b8', padding: 8, width: 220 }}>
      <div style={{ fontWeight: 'bold' }}>{neighbor.remote_sys_name || neighbor.remote_chassis_id}</div>
      <div style={{ fontSize: 12, color: '#475569' }}>{neighbor.remote_port_id || ''}</div>
      <div style={{ fontSize: 12, color: '#475569' }}>confidence: {neighbor.confidence}</div>
      <div style={{ marginTop: 8 }}>
        <button onClick={()=> onAccept(neighbor)} className="btn">Accept</button>
        <button onClick={()=> onReject(neighbor)} className="btn" style={{ marginLeft: 8 }}>Reject</button>
      </div>
    </div>
  )
}
