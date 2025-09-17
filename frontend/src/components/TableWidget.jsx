import React from 'react'

export default function TableWidget({name, config}){
  return (
    <div>
      <h3>{name} (Table)</h3>
      <table style={{width:'100%'}}><tbody><tr><td>Sample</td></tr></tbody></table>
    </div>
  )
}
