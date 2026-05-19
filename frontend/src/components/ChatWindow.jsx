import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { Send, FileText, Loader } from 'lucide-react'
import MessageBubble from './MessageBubble'

export default function ChatWindow({ session }) {
  const [messages, setMessages] = useState([
    {
      role: 'bot',
      text: `I've analysed **${session.filename}**. What would you like to know about this document?`,
      sources: []
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    const question = input.trim()
    if (!question || loading) return

    setMessages(m => [...m, { role: 'user', text: question, sources: [] }])
    setInput('')
    setLoading(true)

    try {
      const res = await axios.post('/api/query', {
        session_id: session.sessionId,
        question
      })
      setMessages(m => [...m, {
        role: 'bot',
        text: res.data.answer,
        sources: res.data.sources
      }])
    } catch (e) {
      setMessages(m => [...m, {
        role: 'bot',
        text: e.response?.data?.detail || 'Something went wrong. Please try again.',
        sources: [],
        error: true
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="chat-wrap">
      <div className="chat-doc-bar">
        <FileText size={15} />
        <span>{session.filename}</span>
      </div>

      <div className="chat-messages">
        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}
        {loading && (
          <div className="bubble bot-bubble loading-bubble">
            <Loader size={16} className="spin" />
            <span>Searching document…</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-row">
        <input
          className="chat-input"
          placeholder="Ask a question about the document…"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && send()}
          disabled={loading}
        />
        <button className="send-btn" onClick={send} disabled={!input.trim() || loading}>
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}