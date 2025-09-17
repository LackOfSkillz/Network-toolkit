import React, {useEffect, useRef} from 'react'
import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

export default function ChartWidget({name, config}){
  const canvasRef = useRef(null)

  useEffect(()=>{
    const ctx = canvasRef.current.getContext('2d')
    const chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['A','B','C','D'],
        datasets: [{
          label: name,
          data: [12, 19, 3, 5],
          backgroundColor: ['#4f46e5', '#06b6d4', '#f97316', '#10b981']
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    })

    return ()=>{
      chart.destroy()
    }
  }, [name])

  return (
    <div>
      <h3>{name} (Chart)</h3>
      <div style={{height:200}}>
        <canvas ref={canvasRef} />
      </div>
    </div>
  )
}
