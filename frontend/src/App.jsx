import { useState } from 'react'
import UploadPanel from './components/UploadPanel'
import ChatWindow from './components/ChatWindow'

export default function App() {
  const [session, setSession] = useState(null)

  const handleUploadSuccess = (sessionData) => {
    setSession(sessionData)
  }

  const handleClear = () => {
    setSession(null)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <div className="logo-wrap">
            <span className="logo-icon">🩺</span>
            <div>
              <h1 className="logo-title">SmartDoc AI</h1>
              <p className="logo-sub">Clinical Document Intelligence</p>
            </div>
          </div>
          {session && (
            <button className="clear-btn" onClick={handleClear}>
              Upload New Document
            </button>
          )}
        </div>
      </header>

      <main className="main">
        {!session ? (
          <UploadPanel onUploadSuccess={handleUploadSuccess} />
        ) : (
          <ChatWindow session={session} />
        )}
      </main>
    </div>
  )
}