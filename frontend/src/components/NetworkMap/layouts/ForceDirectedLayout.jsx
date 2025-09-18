import React, { useEffect, useState, useRef } from 'react'

/**
 * Lightweight force-directed layout renderer.
 * Props:
 * - nodes: [{ id, label?, x?, y? }]
 * - edges: [{ source, target }]
 * - width, height: canvas size
 * - iterations: number of layout iterations (default 200)
 * - onNodeClick: callback(node)
 *
 * This intentionally implements a small, dependency-free simulation suitable
 * for demo and unit tests. Replace with d3-force for production.
 */
export default function ForceDirectedLayout({ nodes = [], edges = [], width = 800, height = 600, iterations = 200, onNodeClick, onNodeContextMenu }){
  const [positions, setPositions] = useState([])
  const containerRef = useRef(null)
  const [size, setSize] = useState({ width, height })

  useEffect(()=>{
    const w = size.width || width
    const h = size.height || height

    // deterministic pseudo-random based on id so snapshots are stable
    function seededVal(key, salt){
      let s = 2166136261 >>> 0
      const str = `${key}:${salt}`
      for(let i=0;i<str.length;i++){
        s ^= str.charCodeAt(i)
        s = Math.imul(s, 16777619) >>> 0
      }
      return (s % 10000) / 10000
    }

    // shallow copy nodes and initialize positions (deterministic)
    const pts = nodes.map((n, i)=>{
      const id = n.id || String(i)
      const x = n.x != null ? n.x : Math.round(seededVal(id, 'x') * w)
      const y = n.y != null ? n.y : Math.round(seededVal(id, 'y') * h)
      return { id, label: n.label || id, x, y, vx: 0, vy: 0 }
    })

    // maps for quick index lookup
    const indexOf = new Map(); pts.forEach((p,i)=> indexOf.set(p.id, i))

    // build link list of index pairs
    const links = edges.map(e=>({ source: indexOf.get(e.source), target: indexOf.get(e.target) })).filter(l=> l.source!=null && l.target!=null)

    // simple physics constants
  const linkDistance = Math.min(w, h) / 6
  const chargeStrength = 4000
    const centerStrength = 0.01
    const damping = 0.85

    for(let iter=0; iter<iterations; iter++){
      // repulsion (O(n^2)) - acceptable for small graphs
      for(let i=0;i<pts.length;i++){
        for(let j=i+1;j<pts.length;j++){
          const a = pts[i], b = pts[j]
          let dx = a.x - b.x
          let dy = a.y - b.y
          let dist2 = dx*dx + dy*dy + 0.01
          let dist = Math.sqrt(dist2)
          // force magnitude
          const force = chargeStrength / dist2
          // normalize
          dx /= dist; dy /= dist
          a.vx += dx * force
          a.vy += dy * force
          b.vx -= dx * force
          b.vy -= dy * force
        }
      }

      // link attraction
      for(const l of links){
        const a = pts[l.source], b = pts[l.target]
        let dx = b.x - a.x
        let dy = b.y - a.y
        let dist = Math.sqrt(dx*dx + dy*dy) + 0.01
        const diff = dist - linkDistance
        const k = 0.1
        const fx = (dx/dist) * diff * k
        const fy = (dy/dist) * diff * k
        a.vx += fx; a.vy += fy
        b.vx -= fx; b.vy -= fy
      }

      // center pull and integrate
      for(const p of pts){
        // toward center
  const cx = w/2, cy = h/2
        p.vx += (cx - p.x) * centerStrength
        p.vy += (cy - p.y) * centerStrength
        // apply damping
        p.vx *= damping; p.vy *= damping
        // integrate
        p.x += p.vx * 0.02
        p.y += p.vy * 0.02
        // clamp to bounds
        p.x = Math.max(0, Math.min(w, p.x))
        p.y = Math.max(0, Math.min(h, p.y))
      }
    }

    setPositions(pts)
  }, [nodes, edges, width, height, iterations, size.width, size.height])

  // Resize observer to update size (non-destructive: use defaults until a non-zero size measured)
  useEffect(()=>{
    const el = containerRef.current
    if(!el) return
    let ro
    function updateSize(rect){
      const nw = Math.round(rect.width)
      const nh = Math.round(rect.height)
      if(nw > 0 && nh > 0){
        setSize({ width: nw, height: nh })
      }
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
      // fallback: measure once
      const rect = el.getBoundingClientRect()
      updateSize(rect)
      window.addEventListener('resize', ()=> updateSize(el.getBoundingClientRect()))
    }
    return ()=>{ if(ro) ro.disconnect() }
  }, [containerRef])

  // Render SVG responsively using viewBox; container controls CSS size
  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%' }}>
      <svg width="100%" height="100%" viewBox={`0 0 ${size.width || width} ${size.height || height}`} preserveAspectRatio="xMidYMid meet" style={{ background: '#f9fafb', border: '1px solid #e5e7eb' }}>
      {/* edges */}
      {edges.map((e, i)=>{
        const s = positions.find(p=>p.id === e.source)
        const t = positions.find(p=>p.id === e.target)
        if(!s || !t) return null
        return <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="#94a3b8" strokeWidth={1} />
      })}

      {/* nodes */}
      {positions.map(p=> (
        <g key={p.id} transform={`translate(${p.x},${p.y})`} style={{ cursor: onNodeClick ? 'pointer' : 'default' }} onClick={()=> onNodeClick && onNodeClick(p)} onContextMenu={(e)=>{ e.preventDefault(); onNodeContextMenu && onNodeContextMenu(p, e) }}>
          <circle r={8} fill="#2563eb" stroke="#1e40af" strokeWidth={1} />
          <text x={12} y={4} fontSize={12} fill="#0f172a">{p.label}</text>
        </g>
      ))}
      </svg>
    </div>
  )
}
