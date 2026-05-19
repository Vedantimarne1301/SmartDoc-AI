import { useState, useRef } from 'react'
import axios from 'axios'
import { Upload, FileText, Loader } from 'lucide-react'

export default function UploadPanel({ onUploadSuccess }) {
  const [dragging, setDragging] = useState(false)
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef()

  const handleFile = (f) => {
    if (!f || !f.name.endsWith('.pdf')) {
      setError('Only PDF files are supported.')
      return
    }
    setError('')
    setFile(f)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setError('')
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      onUploadSuccess({ sessionId: res.data.session_id, filename: res.data.filename })
    } catch (e) {
      setError(e.response?.data?.detail || 'Upload failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-wrap">
      <div className="upload-hero">
        <h2 className="upload-title">Upload a clinical document</h2>
        <p className="upload-sub">Ask questions about patient records, lab reports, or any medical PDF — answers are grounded in your document.</p>
      </div>

      <div
        className={`dropzone ${dragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {file ? (
          <div className="file-preview">
            <FileText size={32} />
            <div>
              <p className="file-name">{file.name}</p>
              <p className="file-size">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>
        ) : (
          <div className="dropzone-idle">
            <Upload size={32} />
            <p>Drag and drop your PDF here</p>
            <span>or click to browse</span>
          </div>
        )}
      </div>

      {error && <p className="upload-error">{error}</p>}

      <button
        className="upload-btn"
        onClick={handleUpload}
        disabled={!file || loading}
      >
        {loading ? <><Loader size={16} className="spin" /> Processing document…</> : 'Analyse Document'}
      </button>

      <div className="disclaimer">
        🔒 Your document is processed in memory and never stored permanently.
      </div>
    </div>
  )
}