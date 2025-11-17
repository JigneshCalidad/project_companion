import React, { useState } from 'react'
import axios from 'axios'
import '../App.css'

function Conversation() {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)
  const [history, setHistory] = useState([])

  const askQuestion = async (e) => {
    e.preventDefault()
    if (!question.trim()) return

    setLoading(true)
    try {
      const res = await axios.post('/api/ask', { question })
      setResponse(res.data)
      setHistory([...history, { question, response: res.data }])
      setQuestion('')
    } catch (error) {
      console.error('Error asking question:', error)
      alert('Error: Could not get response. Is the server running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1>Ask About Your Project</h1>

      <form onSubmit={askQuestion}>
        <input
          type="text"
          className="input"
          placeholder="Ask a question about your codebase..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="button" disabled={loading || !question.trim()}>
          {loading ? 'Asking...' : 'Ask'}
        </button>
      </form>

      {response && (
        <div style={{ marginTop: '2rem' }}>
          <div className="card">
            <h3>Question</h3>
            <p>{response.question}</p>
          </div>

          <div className="card">
            <h3>Answer</h3>
            <p>Found {response.total_matches} matches</p>

            {response.matches && response.matches.length > 0 && (
              <div style={{ marginTop: '1rem' }}>
                <h4>Matches:</h4>
                <ul style={{ marginLeft: '1.5rem', marginTop: '0.5rem' }}>
                  {response.matches.slice(0, 10).map((match, idx) => (
                    <li key={idx} style={{ marginBottom: '0.5rem' }}>
                      <strong>{match.label}</strong> ({match.type})
                      {match.file_path && <span style={{ color: '#666' }}> - {match.file_path}</span>}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {response.related && response.related.length > 0 && (
              <div style={{ marginTop: '1rem' }}>
                <h4>Related:</h4>
                <ul style={{ marginLeft: '1.5rem', marginTop: '0.5rem' }}>
                  {response.related.slice(0, 5).map((rel, idx) => (
                    <li key={idx} style={{ marginBottom: '0.5rem' }}>
                      <strong>{rel.label}</strong> ({rel.type})
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}

      {history.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h3>History</h3>
          {history.slice().reverse().map((item, idx) => (
            <div key={idx} className="card" style={{ marginTop: '1rem' }}>
              <p><strong>Q:</strong> {item.question}</p>
              <p style={{ marginTop: '0.5rem' }}>
                <strong>A:</strong> Found {item.response.total_matches} matches
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Conversation

