import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.css'

const API_BASE = 'https://finsolve-backend-261456487410.southamerica-east1.run.app'

const ROLE_INFO = {
  engineering: {
    color: '#2563EB',
    icon: '🛠️',
    label: 'Engineering',
    samples: ["What's our engineering deployment process?", 'Summarize our technical architecture.'],
  },
  finance: {
    color: '#059669',
    icon: '💰',
    label: 'Finance',
    samples: ['What was covered in the quarterly financial report?', 'What are our marketing expenses this year?'],
  },
  marketing: {
    color: '#DB2777',
    icon: '📣',
    label: 'Marketing',
    samples: ['How did the Q2 2024 campaign perform?', 'What are our key marketing metrics?'],
  },
  hr: {
    color: '#7C3AED',
    icon: '🧑‍💼',
    label: 'HR',
    samples: ['What is the leave policy?', 'What are the responsibilities of HR?'],
  },
  general: {
    color: '#6B7280',
    icon: '🏢',
    label: 'General',
    samples: ['What is the leave policy?', "What are the company's core values?"],
  },
  'c-level': {
    color: '#D97706',
    icon: '👑',
    label: 'C-Level',
    samples: ["Give a summary of engineering's development process.", 'What was covered in the quarterly financial report?'],
  },
}
const DEFAULT_ROLE_INFO = { color: '#6B7280', icon: '👤', label: 'Employee', samples: [] }

function AppLogo() {
  return (
    <svg width="42" height="42" viewBox="0 0 40 40" fill="none" aria-hidden="true">
      <rect width="40" height="40" rx="10" fill="#4F46E5" />
      <path d="M20 9L28 13V19C28 25 24.5 29.5 20 31C15.5 29.5 12 25 12 19V13L20 9Z" fill="white" fillOpacity="0.92" />
      <path d="M17 20L19 22L23.5 17" stroke="#4F46E5" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [user, setUser] = useState(null)
  const [loginError, setLoginError] = useState('')
  const [loggingIn, setLoggingIn] = useState(false)
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)

  const authHeader = () => 'Basic ' + btoa(`${username}:${password}`)

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoginError('')
    setLoggingIn(true)
    try {
      const res = await fetch(`${API_BASE}/me`, {
        headers: { Authorization: authHeader() },
      })
      if (!res.ok) {
        setLoginError('Invalid username or password.')
        return
      }
      setUser(await res.json())
    } catch {
      setLoginError('Could not reach the backend. Is it running?')
    } finally {
      setLoggingIn(false)
    }
  }

  const handleLogout = () => {
    setUser(null)
    setUsername('')
    setPassword('')
    setMessages([])
  }

  const handleAsk = async (e, presetQuestion) => {
    if (e) e.preventDefault()
    const asked = presetQuestion ?? question
    if (!asked.trim()) return
    setQuestion('')
    setMessages((prev) => [...prev, { role: 'user', text: asked }])
    setLoading(true)
    try {
      const url = `${API_BASE}/chat?message=${encodeURIComponent(asked)}`
      const res = await fetch(url, { method: 'POST', headers: { Authorization: authHeader() } })
      const data = await res.json()
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: data.answer, sources: data.sources, blocked: data.blocked },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: 'Something went wrong reaching the backend.', sources: [], blocked: true },
      ])
    } finally {
      setLoading(false)
    }
  }

  if (!user) {
    return (
      <div className="login-screen">
        <div className="login-card">
          <AppLogo />
          <h1>FinSolve Assistant</h1>
          <p className="tagline">
            Ask questions in plain English and get answers grounded in your company's real documents — every
            search is automatically limited to what your role is allowed to see.
          </p>
          <form onSubmit={handleLogin} className="login-form">
            <input
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loggingIn}
            />
            <input
              placeholder="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loggingIn}
            />
            <button type="submit" disabled={loggingIn}>
              {loggingIn ? (
                <>
                  <span className="spinner" /> Logging in…
                </>
              ) : (
                'Log in'
              )}
            </button>
            {loginError && <p className="error">{loginError}</p>}
          </form>
        </div>
      </div>
    )
  }

  const roleInfo = ROLE_INFO[user.role] || DEFAULT_ROLE_INFO

  return (
    <div className="chat-screen">
      <header>
        <div className="who">
          <span className="role-icon" style={{ background: roleInfo.color }}>
            {roleInfo.icon}
          </span>
          <div>
            <strong>{user.username}</strong>
            <span className="role-badge" style={{ background: roleInfo.color }}>
              {roleInfo.label}
            </span>
            <div className="allowed">Can access: {user.allowed_departments.join(', ')}</div>
          </div>
        </div>
        <button className="logout-btn" onClick={handleLogout}>
          Log out
        </button>
      </header>

      {messages.length === 0 && roleInfo.samples.length > 0 && (
        <div className="samples">
          <span className="samples-label">Try asking:</span>
          {roleInfo.samples.map((q) => (
            <button key={q} className="sample-chip" onClick={() => handleAsk(null, q)}>
              {q}
            </button>
          ))}
        </div>
      )}

      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`bubble-row ${m.role}`}>
            <span className="avatar">{m.role === 'user' ? '🧑' : m.blocked ? '🚫' : '🤖'}</span>
            <div className={`bubble ${m.role} ${m.blocked ? 'blocked' : ''}`}>
              {m.role === 'assistant' ? (
                <div className="markdown">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.text}</ReactMarkdown>
                </div>
              ) : (
                <p>{m.text}</p>
              )}
              {m.sources && m.sources.length > 0 && (
                <div className="sources">
                  {m.sources.map((s) => (
                    <span key={s} className="source-chip">
                      📄 {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="bubble-row assistant">
            <span className="avatar">🤖</span>
            <div className="bubble assistant thinking">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleAsk} className="ask-form">
        <input placeholder="Ask a question…" value={question} onChange={(e) => setQuestion(e.target.value)} />
        <button type="submit" disabled={loading}>
          Send
        </button>
      </form>
    </div>
  )
}

export default App
