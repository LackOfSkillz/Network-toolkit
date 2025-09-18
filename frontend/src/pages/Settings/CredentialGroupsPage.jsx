import React, {useEffect, useState} from 'react'
import axios from 'axios'
import EmptyState from '../../components/EmptyState'

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
      {groups.length === 0 ? (
        <EmptyState title="No credential groups" message="Create a credential group to reuse across endpoints." />
      ) : (
        <ul>
          {groups.map(g=> <li key={g.id}>{g.name} ({g.username || '—'})</li>)}
        </ul>
      )}
    </div>
  )
}
