/**
 * Storybook stories for ForceDirectedLayout
 *
 * Demo-only content for layout visualization. No functional changes.
 */
import React from 'react'
import ForceDirectedLayout from './ForceDirectedLayout'

export default { title: 'NetworkMap/ForceDirectedLayout', component: ForceDirectedLayout }

const nodes = [ { id: 'A', label: 'Router A' }, { id: 'B', label: 'Switch B' }, { id: 'C', label: 'Server C' } ]
const edges = [ { source: 'A', target: 'B' }, { source: 'B', target: 'C' } ]

export const Desktop = () => (
  <div style={{ width: 700, height: 240 }}>
    <ForceDirectedLayout nodes={nodes} edges={edges} />
  </div>
)

export const Tablet = () => (
  <div style={{ width: '100%', height: 200 }}>
    <ForceDirectedLayout nodes={nodes} edges={edges} />
  </div>
)
