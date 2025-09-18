import React, { useMemo, useRef, useState, useEffect } from 'react'

/**
 * HierarchicalLayout
 *
 * A compact top-down layout component used for the demo map preview.
 * These comments are explanatory only and make the file friendlier to
 * non-developers; they do not change behavior.
 */
export default function HierarchicalLayout({ nodes = [], width = 800, height = 600, onNodeClick }){
  const containerRef = useRef(null)
  const [size, setSize] = useState({ width, height })
  // Build parent -> children map and find roots
  const { levels } = useMemo(()=>{
    const byId = new Map(nodes.map(n=>[n.id, { ...n, children: [] }]))
    const roots = []
    for(const n of byId.values()){
      if(n.parent && byId.has(n.parent)){
        byId.get(n.parent).children.push(n)
      } else {
        roots.push(n)
      }
    }

    const levels = []
    function dfs(list, depth){
      if(!levels[depth]) levels[depth] = []
      for(const node of list){
        levels[depth].push(node)
        if(node.children && node.children.length) dfs(node.children, depth+1)
      }
    }
    dfs(roots, 0)
    return { levels }
  }, [nodes])

  // compute positions per level (use measured size if available)
  const nodePositions = []
  const w = size.width || width
  const h = size.height || height
  const levelCount = Math.max(1, levels.length)
  const levelHeight = h / (levelCount + 1)
  for(let d=0; d<levels.length; d++){
    const row = levels[d]
    const count = Math.max(1, row.length)
    const spacing = w / (count + 1)
    for(let i=0;i<row.length;i++){
      const x = spacing * (i+1)
      const y = levelHeight * (d+1)
      nodePositions.push({ id: row[i].id, x, y, label: row[i].label || row[i].id })
    }
  }

  useEffect(()=>{
    const el = containerRef.current
    if(!el) return
    let ro
    function updateSize(rect){
      const nw = Math.round(rect.width)
      const nh = Math.round(rect.height)
      if(nw > 0 && nh > 0){ setSize({ width: nw, height: nh }) }
    }
    if(typeof ResizeObserver !== 'undefined'){
      ro = new ResizeObserver(entries=>{
        for(const entry of entries){
          const cr = entry.contentRect || entry.borderBoxSize && entry.borderBoxSize[0] || { width: entry.contentRect?.width || 0, height: entry.contentRect?.height || 0 }
          updateSize(cr)
        }
      })
      ro.observe(el)
    } else {
      updateSize(el.getBoundingClientRect())
      window.addEventListener('resize', ()=> updateSize(el.getBoundingClientRect()))
    }
    return ()=>{ if(ro) ro.disconnect() }
  }, [containerRef])

  // helper to find coords
  const find = id => nodePositions.find(n=>n.id===id)

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%' }}>
      <svg width="100%" height="100%" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="xMidYMid meet" style={{ background: '#fff', border: '1px solid #e6e6e6' }}>
      {/* edges: draw from child to parent */}
      {nodes.map((n, i)=>{
        if(!n.parent) return null
        const a = find(n.id)
        const b = find(n.parent)
        if(!a || !b) return null
        return <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="#cbd5e1" strokeWidth={1} />
      })}

      {/* nodes */}
      {nodePositions.map(p=> (
        <g key={p.id} transform={`translate(${p.x},${p.y})`} onClick={()=> onNodeClick && onNodeClick(p)} style={{ cursor: onNodeClick ? 'pointer' : 'default' }}>
          <rect x={-30} y={-12} width={60} height={24} rx={6} fill="#10b981" />
          <text x={0} y={4} fontSize={12} fill="#042f2e" textAnchor="middle">{p.label}</text>
        </g>
      ))}
    </svg>
    </div>
  )
}
