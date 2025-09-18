import React, { useCallback, useRef, useState } from 'react'

/**
 * DragDropUploader
 *
 * Minimal drag-and-drop file uploader used in the demo. It POSTs files
 * to `uploadUrl`. This comment is for beginners and doesn't affect
 * behavior.
 */
import React, { useCallback, useRef, useState } from 'react'

/**
 * DragDropUploader
 * Props:
 * - uploadUrl (string) endpoint to POST files to
 * - onComplete(files) callback when upload finishes
 * - accept: mime types
 * - multiple: boolean
 */
export default function DragDropUploader({ uploadUrl = '/upload', onComplete, accept='*/*', multiple=true }){
  const [dragOver, setDragOver] = useState(false)
  const [progress, setProgress] = useState(null)
  const inputRef = useRef(null)

  const uploadFiles = useCallback(async (files)=>{
    // simple upload via fetch; for progress, use XMLHttpRequest
    const fd = new FormData()
    for(const f of files) fd.append('files', f)

    // try XHR to get progress events
    return new Promise((resolve)=>{
      const xhr = new XMLHttpRequest()
      xhr.open('POST', uploadUrl)
      xhr.upload.onprogress = (e)=>{
        if(e.lengthComputable) setProgress(Math.round((e.loaded / e.total) * 100))
      }
      xhr.onload = ()=>{
        if(xhr.status >= 200 && xhr.status < 300){
          try{ const resp = JSON.parse(xhr.responseText); onComplete && onComplete(resp); resolve({ ok: true, resp }) }catch(e){ onComplete && onComplete(null); resolve({ ok: true }) }
        } else {
          // fallback: persist to localStorage
          try{ const arr = Array.from(files).map(f=>({ name: f.name, size: f.size, type: f.type })); localStorage.setItem('uploadedFiles', JSON.stringify(arr)) }catch(e){}
          onComplete && onComplete(null)
          resolve({ ok: false })
        }
      }
      xhr.onerror = ()=>{
        // fallback to localStorage
        try{ const arr = Array.from(files).map(f=>({ name: f.name, size: f.size, type: f.type })); localStorage.setItem('uploadedFiles', JSON.stringify(arr)) }catch(e){}
        onComplete && onComplete(null)
        resolve({ ok: false })
      }
      xhr.send(fd)
    })
  }, [uploadUrl, onComplete])

  function handleDrop(e){
    e.preventDefault()
    setDragOver(false)
    const files = e.dataTransfer.files
    if(files && files.length) uploadFiles(files)
  }

  function handleFilesSelected(e){
    const files = e.target.files
    if(files && files.length) uploadFiles(files)
  }

  return (
    <div>
      <div onDragOver={(e)=>{ e.preventDefault(); setDragOver(true) }} onDragLeave={()=> setDragOver(false)} onDrop={handleDrop} style={{ border: '2px dashed #9ca3af', padding:20, textAlign:'center', background: dragOver ? '#f1f5f9' : 'transparent', cursor: 'pointer' }} onClick={()=> inputRef.current && inputRef.current.click()}>
        <input ref={inputRef} type="file" style={{ display: 'none' }} onChange={handleFilesSelected} accept={accept} multiple={multiple} />
        <div>Drag & drop files here or click to select</div>
        {progress !== null && <div style={{marginTop:8}}>Upload progress: {progress}%</div>}
      </div>
    </div>
  )
}
