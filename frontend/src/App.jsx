import { useState } from 'react'
import './App.css'

const API_BASE = 'http://127.0.0.1:8000'

function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [user, setUser] = useState(null)
  const [loginError, setLoginError] = useState('')
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)

  const authHeader = () => 'Basic ' + btoa(`${username}:${password}`)

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoginError('')
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
    }
  }

  const handleLogout = () => {
    setUser(null)
    setUsername('')
    setPassword('')
    setMessages([])
  }

  const handleAsk = async (e) => {
    e.preventDefault()
    if (!question.trim()) return
    const asked = question
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
        <h1>FinSolve Assistant</h1>
        <form onSubmit={handleLogin} className="login-form">
          <input placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <input
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit">Log in</button>
          {loginError && <p className="error">{loginError}</p>}
        </form>
      </div>
    )
  }

  return (
    <div className="chat-screen">
      <header>
        <div>
          <strong>{user.username}</strong>
          <span className="role-badge">{user.role}</span>
        </div>
        <div className="allowed">Can access: {user.allowed_departments.join(', ')}</div>
        <button onClick={handleLogout}>Log out</button>
      </header>

      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`bubble ${m.role} ${m.blocked ? 'blocked' : ''}`}>
            <p>{m.text}</p>
            {m.sources && m.sources.length > 0 && <div className="sources">Sources: {m.sources.join(', ')}</div>}
          </div>
        ))}
        {loading && <div className="bubble assistant">Thinking…</div>}
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
