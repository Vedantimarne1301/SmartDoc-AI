export default function MessageBubble({ message }) {
  const isBot = message.role === 'bot'

  return (
    <div className={`bubble-wrap ${isBot ? 'bot-wrap' : 'user-wrap'}`}>
      {isBot && <div className="avatar">🩺</div>}
      <div className={`bubble ${isBot ? 'bot-bubble' : 'user-bubble'} ${message.error ? 'error-bubble' : ''}`}>
        <p className="bubble-text">{message.text}</p>
        {isBot && message.sources?.length > 0 && (
          <div className="sources">
            <span className="sources-label">Sources:</span>
            {message.sources.map((s, i) => (
              <span key={i} className="source-tag">{s}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}