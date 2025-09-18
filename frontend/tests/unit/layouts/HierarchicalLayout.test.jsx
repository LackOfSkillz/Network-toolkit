import React from 'react'
import { render } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import HierarchicalLayout from '../../../src/components/NetworkMap/layouts/HierarchicalLayout'

describe('HierarchicalLayout snapshots', ()=>{
  const nodes = [ { id: 'root' }, { id: 'c1', parent: 'root' }, { id: 'c2', parent: 'root' } ]

  it('matches desktop snapshot', ()=>{
    const { container } = render(
      <div style={{ width: '700px', height: '240px' }}>
        <HierarchicalLayout nodes={nodes} />
      </div>
    )
    expect(container.querySelector('svg')).toMatchSnapshot()
  })

  it('matches tablet snapshot', ()=>{
    const { container } = render(
      <div style={{ width: '100%', height: '200px' }}>
        <HierarchicalLayout nodes={nodes} />
      </div>
    )
    expect(container.querySelector('svg')).toMatchSnapshot()
  })
})
