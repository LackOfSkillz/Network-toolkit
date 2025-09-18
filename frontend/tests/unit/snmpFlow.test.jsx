import React from 'react'

// mock theme provider used by DashboardPage (ThemeToggle calls useTheme)
vi.mock('../../src/theme/themeProvider', () => ({
  useTheme: () => ({ theme: 'light', toggleTheme: () => {} })
}))

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import DashboardPage from '../../src/pages/DashboardPage'

// adapt to Vitest environment: use vi mock and globals

beforeEach(()=>{
  global.fetch = vi.fn()
})

afterEach(()=>{
  vi.restoreAllMocks()
})

test('SNMP collect flow shows suggestions and accept calls API', async ()=>{
  // mock collect response
  global.fetch
    // initial widgets fetch
    .mockResolvedValueOnce({ ok: true, json: async ()=> ([]) })
    // collect
    .mockResolvedValueOnce({ ok: true, json: async ()=> ({ collector_run_id: 999, saved: 1 }) })
    // neighbors
    .mockResolvedValueOnce({ ok: true, json: async ()=> ({ device_id: 1, neighbors: [ { id: 10, remote_sys_name: 'leaf-1', remote_chassis_id: '00:11:22:33:44:55', remote_mgmt_ips: ['10.0.0.5'], confidence: 0.9 } ] }) })
    // accept
    .mockResolvedValueOnce({ ok: true, json: async ()=> ({ accepted: true, device_id: 42, created: true, link_id: 7 }) })

  const { container } = render(<DashboardPage />)

  // open context menu by simulating right-click on the map overlay div
  const overlay = container.querySelector('.map-overlay')
  expect(overlay).toBeTruthy()
  fireEvent.contextMenu(overlay, { clientX: 100, clientY: 50 })

  // click SNMP Options in the context menu (it appears as text)
  const snmpItem = await screen.findByText('SNMP Options')
  fireEvent.click(snmpItem)

  // modal should open with Collect button
  const collectButton = await screen.findByText('Collect LLDP/CDP')
  fireEvent.click(collectButton)

  // wait for suggestion to appear (neighbor's name)
  await waitFor(()=> expect(screen.getByText('leaf-1')).toBeTruthy())

  // click Accept on the suggestion
  const accept = screen.getByText('Accept')
  fireEvent.click(accept)

  // ensure fetch was called for accept (fourth call: widgets, collect, neighbors, accept)
  await waitFor(()=> expect(global.fetch).toHaveBeenCalledTimes(4))
})
