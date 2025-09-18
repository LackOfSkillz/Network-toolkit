/**
 * Storybook stories for HierarchicalLayout
 *
 * These are demo stories used by Storybook. They illustrate how the
 * HierarchicalLayout component arranges nodes top-down.
 */
import React from 'react'
import HierarchicalLayout from './HierarchicalLayout'

export default { title: 'NetworkMap/HierarchicalLayout', component: HierarchicalLayout }

const nodes = [ { id: 'root', label: 'Network' }, { id: 'r1', label: 'Region 1', parent: 'root' }, { id: 'r2', label: 'Region 2', parent: 'root' } ]

export const Desktop = () => (
  <div style={{ width: 700, height: 240 }}>
    <HierarchicalLayout nodes={nodes} />
  </div>
)

export const Tablet = () => (
  <div style={{ width: '100%', height: 200 }}>
    <HierarchicalLayout nodes={nodes} />
  </div>
)
