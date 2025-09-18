import React, {useEffect, useState} from 'react'
import axios from 'axios'

export default function CredentialGroupsPage(){
  const [groups, setGroups] = useState([])

  useEffect(()=>{
    async function load(){
      try{
        const res = await axios.get('/api/credential-groups')
        setGroups(res.data)
      }catch(e){
        console.error(e)
      }
    }
    load()
  },[])

  return (
    <div>
      <h2>Credential Groups</h2>
      <ul>
        {groups.map(g=> <li key={g.id}>{g.name} ({g.username || '—'})</li>)}
      </ul>
    </div>
  )
}
