/**
 * WelcomeTour
 *
 * A tiny multi-step tour used to introduce the UI. Documented here to
 * help non-developers understand its role.
 */
import React, {useState, useEffect} from 'react'

export default function WelcomeTour({onClose}){
  const [step, setStep] = useState(0)

  useEffect(()=>{
    // noop
  },[])

  const steps = [
    'Welcome to Network Toolkit — this short tour will get you started.',
    'Use the Dashboard to view saved widgets and live data.',
    'Open Settings to configure credential groups and endpoints.'
  ]

  function next(){
    if(step >= steps.length -1){
      localStorage.setItem('seenWelcomeTour','1')
      onClose?.()
    }else{
      setStep(s => s+1)
    }
  }

  function skip(){
    localStorage.setItem('seenWelcomeTour','1')
    onClose?.()
  }

  return (
    <div style={{position:'fixed', left:20, right:20, top:60, padding:20, background:'#fff', border:'1px solid #ddd', zIndex:1000}}>
      <h3>Getting started</h3>
      <p>{steps[step]}</p>
      <div style={{textAlign:'right'}}>
        <button onClick={skip} style={{marginRight:8}}>Skip</button>
        <button onClick={next}>{step === steps.length -1 ? 'Done' : 'Next'}</button>
      </div>
    </div>
  )
}
