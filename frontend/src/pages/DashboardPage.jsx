import React, {useEffect, useState} from 'react'
import ChartWidget from '../components/ChartWidget'
import TableWidget from '../components/TableWidget'

export default function DashboardPage(){
  const [widgets, setWidgets] = useState([])

  useEffect(()=>{
    const token = localStorage.getItem('authToken')
    const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
    fetch('/dashboard/widgets', { headers }).then(r=>{
      if(!r.ok) return []
      return r.json()
    }).then(setWidgets).catch(()=>setWidgets([]))
  }, [])

  return (
    <div>
      <h1>Dashboard</h1>
      {widgets.map(w=> (
        <div key={w.id} style={{border:'1px solid #ccc', padding:10, margin:10}}>
          {w.type === 'chart' ? <ChartWidget config={{}} name={w.name}/> : <TableWidget config={{}} name={w.name}/>}
        </div>
      ))}
    </div>
  )
}
