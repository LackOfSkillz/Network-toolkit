import React from 'react'

/**
 * AnnotationBox: renders a titled annotation rectangle with optional description.
 * Props:
 * - id, x, y, width, height, title, description
 * - onClick(id), onDelete(id), onEdit(id)
 * - style overrides
 */
export default function AnnotationBox({ id, x=0, y=0, width=120, height=60, title='', description='', onClick, onDelete, onEdit, style }){
  const boxStyle = {
    pointerEvents: 'visiblePainted',
  }

  return (
    <g transform={`translate(${x},${y})`} style={boxStyle}>
      <rect x={0} y={0} width={width} height={height} rx={6} fill="rgba(255,249,196,0.9)" stroke="#f59e0b" strokeWidth={1} />
      <text x={8} y={18} fontSize={12} fontWeight={600} fill="#92400e">{title}</text>
      {description && <text x={8} y={36} fontSize={11} fill="#92400e">{description}</text>}
      <g transform={`translate(${width-28},4)`} style={{ cursor: 'pointer' }} onClick={(e)=>{ e.stopPropagation(); onEdit && onEdit(id) }}>
        <rect x={0} y={0} width={12} height={12} rx={2} fill="#fde68a" stroke="#f59e0b" />
      </g>
      <g transform={`translate(${width-14},4)`} style={{ cursor: 'pointer' }} onClick={(e)=>{ e.stopPropagation(); onDelete && onDelete(id) }}>
        <rect x={0} y={0} width={12} height={12} rx={2} fill="#fecaca" stroke="#ef4444" />
      </g>
      <rect x={0} y={0} width={width} height={height} fillOpacity={0} onClick={()=> onClick && onClick(id)} />
    </g>
  )
}
