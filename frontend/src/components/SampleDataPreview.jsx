/**
 * SampleDataPreview
 *
 * Small utility component that renders a preview of a sample data item
 * used by the dashboard demo. Only documented here; no changes to logic.
 */
import React from 'react'

export default function SampleDataPreview({ data }){
  if(!data) return null
  return (
    <div style={{border:'1px solid #eee', padding:8, background:'#fafafa', marginBottom:8}}>
      <strong>Sample payload preview</strong>
      <pre style={{whiteSpace:'pre-wrap', maxHeight:200, overflow:'auto'}}>{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}
