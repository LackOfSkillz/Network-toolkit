// Minimal sample data loader for demos.
// Tries to POST to known backend endpoints and falls back to localStorage when unavailable.

const sampleWidgets = [
  { id: 'w-1', name: 'Traffic Overview', type: 'chart', config: { series: [1,2,3,4] } },
  { id: 'w-2', name: 'Top Talkers', type: 'table', config: { rows: [] } }
]

const sampleSavedViews = [
  { id: 'sv-1', name: 'Default View', layout: { columns: 2 } }
]

const sampleConfigurations = [
  { id: 'c-1', name: 'Site A Config', devices: [{ id: 'd1', hostname: 'rtr1' }] }
]

const sampleCredentialGroups = [
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

export async function loadSampleData(){
  const results = { widgets: null, savedViews: null, configurations: null, credentialGroups: null }

  // widgets
  const widgetsResult = await tryPost('/dashboard/widgets', sampleWidgets[0])
  results.widgets = widgetsResult

  // saved views
  const sv = await tryPost('/saved-views', sampleSavedViews[0])
  results.savedViews = sv

  // configurations
  const cfg = await tryPost('/configurations', sampleConfigurations[0])
  results.configurations = cfg

  // credential groups
  const cg = await tryPost('/credential-groups', sampleCredentialGroups[0])
  results.credentialGroups = cg

  // If backend unavailable for any, persist sample to localStorage for frontend demo.
  if(!results.widgets || !results.savedViews || !results.configurations || !results.credentialGroups){
    localStorage.setItem('sampleData', JSON.stringify({ widgets: sampleWidgets, savedViews: sampleSavedViews, configurations: sampleConfigurations, credentialGroups: sampleCredentialGroups }))
  }

  return results
}

export default { loadSampleData }
