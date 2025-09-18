/**
 * ContextMenu
 *
 * Small helper to render a contextual menu on the map preview. Items are
 * shallow objects with `id`, `label` and `onClick`.
 */
import React from 'react'

export default function ContextMenu({ items = [], position = null, onClose }){
  if(!position) return null
  const style = { position: 'absolute', left: position.x, top: position.y, background: '#fff', border: '1px solid #e5e7eb', boxShadow: '0 2px 6px rgba(0,0,0,0.08)', zIndex: 1000 }
  return (
    <div style={style} onMouseLeave={onClose}>
      {items.map(it=> (
        <div key={it.id} style={{ padding: '8px 12px', cursor: 'pointer' }} onClick={()=>{ it.onClick(); onClose && onClose() }}>{it.label}</div>
      ))}
    </div>
  )
}
