/**
 * sampleDataLoader.js
 *
 * Provides demo/sample data used by the frontend. It attempts to POST a
 * representative payload to the backend; when the backend is unavailable
 * it falls back to storing sample data in localStorage so the UI can
 * still demonstrate behavior offline.
 */
// Minimal sample data loader for demos.
// Tries to POST to known backend endpoints and falls back to localStorage when unavailable.

export const sampleWidgets = [
  { id: 'w-1', name: 'Traffic Overview', type: 'chart', config: { series: [1,2,3,4] } },
  { id: 'w-2', name: 'Top Talkers', type: 'table', config: { rows: [] } }
]

export const sampleSavedViews = [
  { id: 'sv-1', name: 'Default View', layout: { columns: 2 } }
]

export const sampleConfigurations = [
  { id: 'c-1', name: 'Site A Config', devices: [{ id: 'd1', hostname: 'rtr1' }] }
]

export const sampleCredentialGroups = [
  { id: 'cg-1', name: 'Read-only', username: 'reader', password: 'password' }
]

async function tryPost(path, payload){
  try{
    const token = localStorage.getItem('authToken')
    const headers = { 'Content-Type': 'application/json' }
    if(token) headers['Authorization'] = `Bearer ${token}`
    const res = await fetch(path, { method: 'POST', headers, body: JSON.stringify(payload) })
    if(!res.ok) throw new Error('non-2xx')
    return await res.json()
  }catch(e){
    return null
  }
}

export async function loadSampleData({ onProgress } = {}){
  const results = { widgets: null, savedViews: null, configurations: null, credentialGroups: null }
  const steps = [
    { name: 'widgets', payload: sampleWidgets[0], path: '/dashboard/widgets' },
    { name: 'savedViews', payload: sampleSavedViews[0], path: '/saved-views' },
    { name: 'configurations', payload: sampleConfigurations[0], path: '/configurations' },
    { name: 'credentialGroups', payload: sampleCredentialGroups[0], path: '/credential-groups' }
  ]

  for(let i=0;i<steps.length;i++){
    const s = steps[i]
    if(onProgress) onProgress({ step: s.name, index: i, total: steps.length })
    const res = await tryPost(s.path, s.payload)
    results[s.name] = res
  }

  // If backend unavailable for any, persist sample to localStorage for frontend demo.
  if(!results.widgets || !results.savedViews || !results.configurations || !results.credentialGroups){
    localStorage.setItem('sampleData', JSON.stringify({ widgets: sampleWidgets, savedViews: sampleSavedViews, configurations: sampleConfigurations, credentialGroups: sampleCredentialGroups }))
  }

  return results
}

export function resetSampleData(){
  localStorage.removeItem('sampleData')
}

export default { loadSampleData, resetSampleData }
