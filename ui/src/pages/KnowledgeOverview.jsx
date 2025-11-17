import React, { useState, useEffect } from 'react'
import api from '../api'
import '../App.css'

function KnowledgeOverview() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [mermaid, setMermaid] = useState('')

  useEffect(() => {
    loadStats()
    loadMermaid()
  }, [])

  const loadStats = async () => {
    try {
      const response = await api.get('/api/graph/statistics')
      setStats(response.data)
    } catch (error) {
      console.error('Error loading stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadMermaid = async () => {
    try {
      const response = await api.get('/api/graph/export/mermaid')
      setMermaid(response.data.mermaid)
    } catch (error) {
      console.error('Error loading mermaid:', error)
    }
  }

  const exportJson = async () => {
    try {
      const response = await api.get('/api/graph/export/json')
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'knowledge-graph.json'
      a.click()
    } catch (error) {
      console.error('Error exporting JSON:', error)
    }
  }

  if (loading) {
    return <div className="page">Loading...</div>
  }

  return (
    <div className="page">
      <h1>Knowledge Graph Overview</h1>

      {stats && (
        <div className="card">
          <h3>Statistics</h3>
          <p>Nodes: {stats.node_count}</p>
          <p>Edges: {stats.edge_count}</p>
          <p>Connected: {stats.is_connected ? 'Yes' : 'No'}</p>
          <p>Components: {stats.components}</p>
        </div>
      )}

      <div style={{ marginTop: '2rem' }}>
        <button className="button" onClick={exportJson}>
          Export JSON
        </button>
      </div>

      {mermaid && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Graph Visualization (Mermaid)</h3>
          <pre style={{ 
            background: '#f8f9fa', 
            padding: '1rem', 
            borderRadius: '4px',
            overflow: 'auto',
            maxHeight: '500px'
          }}>
            {mermaid}
          </pre>
          <p style={{ marginTop: '1rem', color: '#666', fontSize: '0.9rem' }}>
            Copy this Mermaid code to{' '}
            <a href="https://mermaid.live" target="_blank" rel="noopener noreferrer">
              Mermaid Live Editor
            </a>
            {' '}to visualize the graph.
          </p>
        </div>
      )}
    </div>
  )
}

export default KnowledgeOverview

