import React, {useEffect, useState, useCallback} from 'react'
import ChartWidget from '../components/ChartWidget'
import TableWidget from '../components/TableWidget'
import EmptyState from '../components/EmptyState'
import useSocket from '../realtime/useSocket'
import { loadSampleData, resetSampleData, sampleWidgets, sampleSavedViews, sampleConfigurations, sampleCredentialGroups } from '../utils/sampleDataLoader'
import SampleDataPreview from '../components/SampleDataPreview'
import { ForceDirectedLayout, HierarchicalLayout } from '../components/NetworkMap/layouts'
import { AnnotationLayer } from '../components/NetworkMap/Annotations'
import ContextMenu from '../components/NetworkMap/ContextMenu'
import useShortcuts from '../utils/shortcuts'
import { useTheme } from '../theme/themeProvider'
import SNMPOptionsModal from '../components/SNMP/SNMPOptionsModal'
import SuggestionCard from '../components/SNMP/SuggestionCard'

export default function DashboardPage(){
  /**
   * DashboardPage
   *
   * High-level page component that composes widgets and listens for
   * realtime updates. The implementation below is intentionally small —
   * these notes explain the purpose for non-developers.
   */
  const [widgets, setWidgets] = useState([])
  const [loadingSample, setLoadingSample] = useState(false)
  const [sampleStatus, setSampleStatus] = useState(null)
  const [sampleProgress, setSampleProgress] = useState(null)
  const [previewTarget, setPreviewTarget] = useState(null)
  const [layout, setLayout] = useState('force')
  const [annotations, setAnnotations] = useState([])
  const [contextMenu, setContextMenu] = useState(null)
  const [snmpModal, setSnmpModal] = useState({ open: false, device: null })
  const [suggestedNodes, setSuggestedNodes] = useState([])

  // annotation handlers
  function addAnnotation(){
    const id = `a${Date.now()}`
    const ann = { id, x: 50 + Math.random()*300, y: 20 + Math.random()*100, width: 140, height: 60, title: 'Note', description: 'Annotation' }
    setAnnotations(prev => [...prev, ann])
  }

  function deleteAnnotation(id){
    setAnnotations(prev => prev.filter(a=> a.id !== id))
  }

  function editAnnotation(id){
    // simple edit: append a dot to title
    setAnnotations(prev => prev.map(a=> a.id === id ? { ...a, title: a.title + '.' } : a))
  }

  // context menu helpers
  function handleContextMenu(e){
    // only show for the preview area; callers will attach to the overlay div
    e.preventDefault()
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top
    setContextMenu({ x, y, clientX: e.clientX, clientY: e.clientY })
  }

  function closeContextMenu(){ setContextMenu(null) }

  // keyboard shortcuts
  useShortcuts({
    'Shift+A': ()=> addAnnotation(),
    'Shift+L': ()=> setLayout(prev => prev === 'force' ? 'hierarchical' : 'force'),
    'Shift+S': ()=> onLoadSample(),
    'Shift+C': ()=> setAnnotations([]),
  })

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
    setSampleProgress({ step: 0, total: 4 })
    try{
      const res = await loadSampleData({ onProgress: (p)=> setSampleProgress(p) })
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

  function onResetSample(){
    resetSampleData()
    setWidgets([])
    setSampleStatus({ reset: true })
  }

  return (
    <div className="dashboard-root">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <div>
          <ThemeToggle />
        </div>
      </div>
      {/* small sample map preview */}
      <div className="map-card">
        <strong>Map Preview</strong>
        <div className="map-controls">
          <label className="map-label">Layout:</label>
          <select value={layout} onChange={(e)=> setLayout(e.target.value)}>
            <option value="force">Force-directed</option>
            <option value="hierarchical">Hierarchical</option>
          </select>
          <button onClick={addAnnotation} className="btn" style={{marginLeft:12}}>Add Annotation</button>
          <button onClick={()=> setAnnotations([])} className="btn" style={{marginLeft:8}}>Clear Annotations</button>
        </div>
        <div>
          <div className="map-preview" style={{ position: 'relative', width: 700, height: 240 }}>
            {layout === 'force' ? (
              <ForceDirectedLayout nodes={sampleNodes} edges={sampleEdges} onNodeClick={(n)=> alert(`Node: ${n.id}`)} onNodeContextMenu={(n,e)=> { setSnmpModal({ open: true, device: n }); setContextMenu({ x: e.clientX - e.currentTarget.getBoundingClientRect().left, y: e.clientY - e.currentTarget.getBoundingClientRect().top, clientX: e.clientX, clientY: e.clientY }) }} />
            ) : (
              <HierarchicalLayout nodes={hierNodes} onNodeClick={(n)=> alert(`Node: ${n.id}`)} />
            )}
            <div className="map-overlay" style={{ position: 'absolute', left:0, top:0, width:700, height:240, pointerEvents: 'auto' }} onContextMenu={handleContextMenu}>
              <AnnotationLayer annotations={annotations} onClick={(id)=> alert(`Annotation clicked ${id}`)} onDelete={deleteAnnotation} onEdit={editAnnotation} />
              <ContextMenu position={contextMenu ? { x: contextMenu.x, y: contextMenu.y } : null} onClose={closeContextMenu} items={contextMenu ? [
                { id: 'add-annotation', label: 'Add Annotation', onClick: ()=> addAnnotation() },
                { id: 'inspect', label: 'Inspect Position', onClick: ()=> alert(`Position: ${contextMenu.x}, ${contextMenu.y}`) },
                { id: 'snmp', label: 'SNMP Options', onClick: ()=> {
                  // for demo map preview use sampleNodes[0] as device
                  setSnmpModal({ open: true, device: sampleNodes[0] })
                } },
              ] : []} />

              {/* render suggested nodes */}
              {suggestedNodes.map((s, idx)=> (
                <div key={s.id} style={{ position: 'absolute', left: s.x, top: s.y }}>
                  <SuggestionCard neighbor={s.neighbor} onAccept={async (n)=>{
                    // call accept endpoint
                    const token = localStorage.getItem('authToken')
                    const headers = token ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' } : { 'Content-Type': 'application/json' }
                    const resp = await fetch(`/lldp/devices/${sampleNodes[0].id}/neighbors/accept`, { method: 'POST', headers, body: JSON.stringify({ neighbor: n }) })
                    const body = await resp.json()
                    if(resp.ok){
                      // replace suggestion with permanent node
                      setSuggestedNodes(prev => prev.filter(x=> x.id !== s.id))
                      alert(`Accepted: created device ${body.device_id}`)
                    } else {
                      alert('Accept failed: '+ JSON.stringify(body))
                    }
                  }} onReject={(n)=>{
                    setSuggestedNodes(prev => prev.filter(x=> x.id !== s.id))
                  }} />
                </div>
              ))}
              
              <SNMPOptionsModal device={snmpModal.device} open={snmpModal.open} onClose={()=> setSnmpModal({ open:false, device: null })} onCollect={(device, body, neighbors)=>{
                // add suggested nodes as children of the device (place them offset)
                // derive placement from context menu client coords if available
                const baseX = contextMenu ? contextMenu.x : 350
                const baseY = contextMenu ? contextMenu.y : 120
                const newSuggestions = (neighbors.neighbors || []).map((n,i)=> ({ id: `s-${body.collector_run_id}-${i}`, label: n.remote_sys_name || n.remote_chassis_id || `neighbor-${i}`, x: baseX + 30 * Math.cos(i * 1.2) * (i+1), y: baseY + 30 * Math.sin(i * 1.2) * (i+1), neighbor: n }))
                setSuggestedNodes(prev => [...prev, ...newSuggestions])
                setSnmpModal({ open:false, device: null })
              }} />
            </div>
          </div>
        </div>
      </div>
      <div className="controls-row">
        <button onClick={onLoadSample} disabled={loadingSample} className="btn" style={{marginRight:8}}>{loadingSample ? 'Loading...' : 'Load sample data'}</button>
        <button onClick={onResetSample} className="btn" style={{marginRight:8}}>Reset sample data</button>
        <label className="map-label">Preview:</label>
        <select value={previewTarget || ''} onChange={(e)=> setPreviewTarget(e.target.value || null)}>
          <option value="">-- none --</option>
          <option value="widgets">widgets</option>
          <option value="savedViews">savedViews</option>
          <option value="configurations">configurations</option>
          <option value="credentialGroups">credentialGroups</option>
        </select>
        {sampleProgress && <span className="status-text">Step {sampleProgress.index+1}/{sampleProgress.total}: {sampleProgress.step}</span>}
  {sampleStatus && <span className={`status-text ${sampleStatus.error ? 'status-error' : 'status-ok'}`}>{sampleStatus.error ? sampleStatus.error : (sampleStatus.reset ? 'Sample data reset' : 'Sample data loaded')}</span>}
      </div>
      <SampleDataPreview data={previewTarget === 'widgets' ? sampleWidgets[0] : previewTarget === 'savedViews' ? sampleSavedViews[0] : previewTarget === 'configurations' ? sampleConfigurations[0] : previewTarget === 'credentialGroups' ? sampleCredentialGroups[0] : null} />
      {widgets.length === 0 ? (
        <EmptyState title="No widgets" message="You don't have any widgets yet. Add some from the dashboard settings." />
      ) : (
        widgets.map(w=> (
          <div key={w.id} className="widget-card">
            {w.type === 'chart' ? <ChartWidget config={{}} name={w.name}/> : <TableWidget config={{}} name={w.name}/>}
          </div>
        ))
      )}
    </div>
  )
}

function ThemeToggle(){
  const { theme, toggleTheme } = useTheme()
  return (<button onClick={toggleTheme} style={{marginLeft:12}}>Theme: {theme}</button>)
}

// sample graph data for the preview
const sampleNodes = [
  { id: 'A', label: 'Router A' },
  { id: 'B', label: 'Switch B' },
  { id: 'C', label: 'Server C' },
  { id: 'D', label: 'Office D' }
]
const sampleEdges = [ { source: 'A', target: 'B' }, { source: 'B', target: 'C' }, { source: 'B', target: 'D' } ]

const hierNodes = [
  { id: 'root', label: 'Network', parent: null },
  { id: 'r1', label: 'Region 1', parent: 'root' },
  { id: 'r2', label: 'Region 2', parent: 'root' },
  { id: 'h1', label: 'Host 1', parent: 'r1' }
]

