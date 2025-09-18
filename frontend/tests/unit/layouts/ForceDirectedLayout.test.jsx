import React from 'react'
import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import ForceDirectedLayout from '../../../src/components/NetworkMap/layouts/ForceDirectedLayout'

describe('ForceDirectedLayout snapshots', ()=>{
  const nodes = [ { id: 'A' }, { id: 'B' }, { id: 'C' } ]
  const edges = [ { source: 'A', target: 'B' }, { source: 'B', target: 'C' } ]

  it('matches desktop snapshot', ()=>{
    const { container } = render(
      <div style={{ width: '700px', height: '240px' }}>
        <ForceDirectedLayout nodes={nodes} edges={edges} />
      </div>
    )
    expect(container.querySelector('svg')).toMatchSnapshot()
  })

  it('matches tablet snapshot', ()=>{
    const { container } = render(
      <div style={{ width: '100%', height: '200px' }}>
        <ForceDirectedLayout nodes={nodes} edges={edges} />
      </div>
    )
    expect(container.querySelector('svg')).toMatchSnapshot()
  })
})
