import { beforeEach, afterEach, describe, expect, it } from 'vitest'
import { loadSampleData, resetSampleData, sampleWidgets } from '../../../frontend/src/utils/sampleDataLoader'

describe('sampleDataLoader', () => {
  beforeEach(()=>{
    // clear localStorage
    localStorage.clear()
    // mock fetch to fail so loader falls back to localStorage
    global.fetch = async ()=> ({ ok: false })
  })

  afterEach(()=>{
    delete global.fetch
    resetSampleData()
  })

  it('persists sample data when backend unreachable and reports progress', async ()=>{
    const progressEvents = []
    const res = await loadSampleData({ onProgress: (p)=> progressEvents.push(p) })
    expect(progressEvents.length).toBeGreaterThanOrEqual(1)
    // sampleData should be stored in localStorage
    const stored = JSON.parse(localStorage.getItem('sampleData'))
    expect(stored).toBeTruthy()
    expect(stored.widgets[0].name).toEqual(sampleWidgets[0].name)
    expect(res.widgets).toBeNull()
  })
})
