import React, {useEffect, useState, useCallback} from 'react'
import ChartWidget from '../components/ChartWidget'
import TableWidget from '../components/TableWidget'
import EmptyState from '../components/EmptyState'
import useSocket from '../realtime/useSocket'

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

  const handleWidgetUpdated = useCallback((payload)=>{
    // payload expected to be { id, action, widget }
    if(!payload) return
    setWidgets(prev => {
      const { action, widget } = payload
      if(action === 'created') return [widget, ...prev]
      if(action === 'updated') return prev.map(w=> w.id === widget.id ? widget : w)
      if(action === 'deleted') return prev.filter(w=> w.id !== widget.id)
      return prev
    })
  }, [])

  useSocket('widget_updated', handleWidgetUpdated)

  return (
    <div>
      <h1>Dashboard</h1>
      {widgets.length === 0 ? (
        <EmptyState title="No widgets" message="You don't have any widgets yet. Add some from the dashboard settings." />
      ) : (
        widgets.map(w=> (
          <div key={w.id} style={{border:'1px solid #ccc', padding:10, margin:10}}>
            {w.type === 'chart' ? <ChartWidget config={{}} name={w.name}/> : <TableWidget config={{}} name={w.name}/>}
          </div>
        ))
      )}
    </div>
  )
}
