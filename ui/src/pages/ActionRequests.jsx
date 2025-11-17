import React, { useState, useEffect } from 'react'
import axios from 'axios'
import '../App.css'

function ActionRequests() {
  const [actions, setActions] = useState([])
  const [loading, setLoading] = useState(true)
  const [command, setCommand] = useState('')

  useEffect(() => {
    loadActions()
  }, [])

  const loadActions = async () => {
    try {
      const response = await axios.get('/api/actions/pending')
      setActions(response.data)
    } catch (error) {
      console.error('Error loading actions:', error)
    } finally {
      setLoading(false)
    }
  }

  const requestAction = async (e) => {
    e.preventDefault()
    if (!command.trim()) return

    try {
      await axios.post('/api/actions/request', {
        action_type: 'command',
        command: command,
        details: {}
      })
      setCommand('')
      loadActions()
    } catch (error) {
      console.error('Error requesting action:', error)
      alert('Error: Could not request action.')
    }
  }

  const approveAction = async (actionId, approved) => {
    try {
      await axios.post('/api/actions/approve', {
        action_id: actionId,
        approved: approved,
        user: 'ui_user'
      })
      loadActions()
    } catch (error) {
      console.error('Error approving action:', error)
      alert('Error: Could not approve/reject action.')
    }
  }

  if (loading) {
    return <div className="page">Loading...</div>
  }

  return (
    <div className="page">
      <h1>Action Requests</h1>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <h3>Request New Action</h3>
        <form onSubmit={requestAction}>
          <input
            type="text"
            className="input"
            placeholder="Enter command (e.g., ls -la)"
            value={command}
            onChange={(e) => setCommand(e.target.value)}
          />
          <button type="submit" className="button" disabled={!command.trim()}>
            Request Action
          </button>
        </form>
        <p style={{ marginTop: '1rem', color: '#666', fontSize: '0.9rem' }}>
          ⚠️ All actions require approval before execution.
        </p>
      </div>

      <h2>Pending Actions</h2>
      {actions.length === 0 ? (
        <p>No pending actions.</p>
      ) : (
        actions.map((action) => (
          <div key={action.id} className="card">
            <h3>Action #{action.id}</h3>
            <p><strong>Type:</strong> {action.action_type}</p>
            <p><strong>User:</strong> {action.user}</p>
            <p><strong>Command:</strong> {action.details.command || 'N/A'}</p>
            <p><strong>Status:</strong> {action.status}</p>
            <p><strong>Requested:</strong> {new Date(action.timestamp).toLocaleString()}</p>
            <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
              <button
                className="button"
                onClick={() => approveAction(action.id, true)}
              >
                Approve
              </button>
              <button
                className="button button-danger"
                onClick={() => approveAction(action.id, false)}
              >
                Reject
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  )
}

export default ActionRequests

