import React from 'react'

export default function EmptyState({title='No items', message='Nothing to see here yet.', action}){
  return (
    <div style={{padding:20, border:'1px dashed #ddd', textAlign:'center', margin:10}}>
      <h3>{title}</h3>
      <p>{message}</p>
      {action}
    </div>
  )
}
