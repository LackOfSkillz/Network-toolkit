import React from 'react'
import AnnotationBox from './AnnotationBox'

/**
 * AnnotationLayer renders a collection of annotations on top of a map.
 * Props:
 * - annotations: [{ id, x, y, width, height, title, description }]
 * - onClick(id), onDelete(id), onEdit(id)
 */
export default function AnnotationLayer({ annotations = [], onClick, onDelete, onEdit }){
  // Allow pointer events on the overlay so AnnotationBox can receive clicks.
  return (
    <svg width="100%" height="100%" style={{ position: 'absolute', left:0, top:0, pointerEvents: 'auto' }}>
      <g>
        {annotations.map(a => (
          <AnnotationBox key={a.id} {...a} onClick={onClick} onDelete={onDelete} onEdit={onEdit} />
        ))}
      </g>
    </svg>
  )
}
