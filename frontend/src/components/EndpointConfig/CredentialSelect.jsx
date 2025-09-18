/**
 * CredentialSelect
 *
 * Small select control that fetches available credential groups from the
 * backend and exposes a simple onChange callback. Documented for
 * non-developers; no behavior changes.
 */
import React, {useEffect, useState} from 'react'
import axios from 'axios'

export default function CredentialSelect({value, onChange}){
  const [groups, setGroups] = useState([])

  useEffect(()=>{
    async function load(){
      try{
        const res = await axios.get('/api/credential-groups')
        setGroups(res.data)
      }catch(e){
        console.error('failed to load credential groups', e)
      }
    }
    load()
  },[])

  return (
    <select value={value || ''} onChange={e=> onChange?.(e.target.value)}>
      <option value="">-- Select credential group --</option>
      {groups.map(g=> <option key={g.id} value={g.id}>{g.name}</option>)}
    </select>
  )
}
