import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import KnowledgeOverview from './pages/KnowledgeOverview'
import Conversation from './pages/Conversation'
import ActionRequests from './pages/ActionRequests'
import Settings from './pages/Settings'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              Project Companion
            </Link>
            <div className="nav-links">
              <Link to="/">Knowledge</Link>
              <Link to="/conversation">Ask</Link>
              <Link to="/actions">Actions</Link>
              <Link to="/settings">Settings</Link>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<KnowledgeOverview />} />
            <Route path="/conversation" element={<Conversation />} />
            <Route path="/actions" element={<ActionRequests />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

