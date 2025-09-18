import React, {useEffect, useState, useCallback} from 'react'
import ChartWidget from '../components/ChartWidget'
import TableWidget from '../components/TableWidget'
import EmptyState from '../components/EmptyState'
import useSocket from '../realtime/useSocket'
import { loadSampleData } from '../utils/sampleDataLoader'

export default function DashboardPage(){
  const [widgets, setWidgets] = useState([])
  const [loadingSample, setLoadingSample] = useState(false)
  const [sampleStatus, setSampleStatus] = useState(null)

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

  async function onLoadSample(){
    setLoadingSample(true)
    setSampleStatus(null)
    try{
      const res = await loadSampleData()
      setSampleStatus(res)
      // if backend returned widgets, refresh
      if(res && res.widgets){
        // if API returned created widget, reload list
        const token = localStorage.getItem('authToken')
        const headers = token ? { 'Authorization': `Bearer ${token}` } : {}
        fetch('/dashboard/widgets', { headers }).then(r=> r.ok ? r.json() : []).then(setWidgets).catch(()=>{})
      } else {
        // fallback to localStorage sample data
        const s = localStorage.getItem('sampleData')
        if(s) {
          try{ const parsed = JSON.parse(s); setWidgets(parsed.widgets || []) }catch(e){}
        }
      }
    }catch(e){
      setSampleStatus({ error: String(e) })
    } finally { setLoadingSample(false) }
  }

  return (
    <div>
      <h1>Dashboard</h1>
      <div style={{marginBottom:12}}>
        <button onClick={onLoadSample} disabled={loadingSample} style={{marginRight:8}}>{loadingSample ? 'Loading...' : 'Load sample data'}</button>
        {sampleStatus && <span style={{color: sampleStatus.error ? 'red' : 'green'}}>{sampleStatus.error ? sampleStatus.error : 'Sample data loaded'}</span>}
      </div>
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
