import React, { useState, useEffect } from 'react'
import axios from 'axios'
import '../App.css'

function Settings() {
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(true)
  const [enableDynamicScan, setEnableDynamicScan] = useState(false)
  const [readOnlyMode, setReadOnlyMode] = useState(true)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const response = await axios.get('/api/settings')
      setSettings(response.data)
      setEnableDynamicScan(response.data.enable_dynamic_scan)
      setReadOnlyMode(response.data.read_only_mode)
    } catch (error) {
      console.error('Error loading settings:', error)
    } finally {
      setLoading(false)
    }
  }

  const saveSettings = async () => {
    try {
      await axios.post('/api/settings', {
        enable_dynamic_scan: enableDynamicScan,
        read_only_mode: readOnlyMode
      })
      alert('Settings saved!')
      loadSettings()
    } catch (error) {
      console.error('Error saving settings:', error)
      alert('Error: Could not save settings.')
    }
  }

  if (loading) {
    return <div className="page">Loading...</div>
  }

  return (
    <div className="page">
      <h1>Settings</h1>

      <div className="card">
        <h3>Security Settings</h3>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <input
              type="checkbox"
              checked={readOnlyMode}
              onChange={(e) => setReadOnlyMode(e.target.checked)}
            />
            <div>
              <strong>Read-Only Mode</strong>
              <p style={{ color: '#666', fontSize: '0.9rem', marginTop: '0.25rem' }}>
                When enabled, all write actions are blocked. Recommended for safety.
              </p>
            </div>
          </label>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <input
              type="checkbox"
              checked={enableDynamicScan}
              onChange={(e) => setEnableDynamicScan(e.target.checked)}
            />
            <div>
              <strong>Enable Dynamic Scanning</strong>
              <p style={{ color: '#666', fontSize: '0.9rem', marginTop: '0.25rem' }}>
                ⚠️ Allows Playwright-based web application scanning. Requires explicit confirmation.
              </p>
            </div>
          </label>
        </div>

        <button className="button" onClick={saveSettings}>
          Save Settings
        </button>
      </div>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h3>Secrets Management</h3>
        <p style={{ color: '#666', marginBottom: '1rem' }}>
          Store secrets in environment variables or a secure keystore. Never commit secrets to the repository.
        </p>
        <p style={{ fontSize: '0.9rem', color: '#666' }}>
          See <code>SECURITY.md</code> for detailed instructions.
        </p>
      </div>
    </div>
  )
}

export default Settings

