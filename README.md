# 🩺 SmartDoc AI

A RAG-based clinical document intelligence assistant that lets healthcare professionals upload patient records and ask questions — answers are grounded in the document with source citations.

---

## ✨ Features

| Feature | Description |
|---|---|
| **PDF Upload** | Drag and drop or click to upload any clinical PDF |
| **RAG Pipeline** | Retrieval-Augmented Generation using LangChain + FAISS |
| **Source Citations** | Every answer cites the page numbers it was drawn from |
| **Chat History** | Maintains conversation context across multiple questions |
| **Session Management** | UUID-based sessions, safe for multiple simultaneous users |
| **Clinical Guardrails** | Never hallucinates — answers only from document context |

---

## 🔗 Live Demo

👉 [https://vedantimarne13-smartdoc-ai.hf.space](https://vedantimarne13-smartdoc-ai.hf.space)

---

## 🗂 Project Structure
smartdoc-ai/
├── backend/
│   ├── main.py
│   ├── qabot.py
│   ├── requirements.txt
│   └── static/
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── components/
│   │       ├── UploadPanel.jsx
│   │       ├── ChatWindow.jsx
│   │       └── MessageBubble.jsx
│   ├── index.html
│   └── package.json
├── Dockerfile
├── deploy.bat
├── .gitignore
└── README.md

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite |
| Styling | Custom CSS — Lora + Karla fonts, clinical aesthetic |
| Icons | Lucide React |
| HTTP Client | Axios |
| Backend | Python, FastAPI, Uvicorn |
| RAG Framework | LangChain |
| LLM | Groq API — llama-3.1-8b-instant |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Store | FAISS (in-memory) |
| PDF Parsing | PyPDF |
| Deployment | Hugging Face Spaces (Docker) |

---

## ⚙️ Setup Instructions

### Prerequisites

- Python >= 3.11
- Node.js >= 18.x
- A [Groq API key](https://console.groq.com)

---

### Step 1 — Clone the repository

```bash
git clone https://github.com/your-username/smartdoc-ai.git
cd smartdoc-ai
```

---

### Step 2 — Backend setup

```bash
cd backend

# Create and activate virtual environment
python -m venv my-env
my-env\Scripts\activate       # Windows
source my-env/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:
GROQ_API_KEY=your_groq_api_key_here

Start the backend:

```bash
uvicorn main:app --reload --port 8000
```

Backend runs at `http://localhost:8000`

---

### Step 3 — Frontend setup

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

---

### Step 4 — Getting your Groq API key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Navigate to **API Keys → Create API Key**
4. Copy the key into `backend/.env` as `GROQ_API_KEY`

---

## 🔌 API Reference

### `POST /api/upload`
Uploads and processes a PDF document.

**Request:** `multipart/form-data` with a `file` field (PDF only)

**Response:**
```json
{
  "session_id": "uuid-string",
  "filename": "patient_record.pdf",
  "message": "PDF processed successfully"
}
```

---

### `POST /api/query`
Asks a question about the uploaded document.

**Request body:**
```json
{
  "session_id": "uuid-string",
  "question": "What medications is the patient on?"
}
```

**Response:**
```json
{
  "answer": "The patient is currently prescribed...",
  "sources": ["Page 3", "Page 5"]
}
```

---

### `DELETE /api/session/{session_id}`
Clears a session from memory.

---

### `GET /api/health`
Health check endpoint.

**Response:**
```json
{ "status": "ok" }
```

---

## 🧠 Approach Explanation

### RAG Pipeline
User uploads PDF
↓
PyPDF loads and parses pages
↓
RecursiveCharacterTextSplitter chunks text (500 chars, 50 overlap)
↓
all-MiniLM-L6-v2 generates embeddings for each chunk
↓
FAISS builds an in-memory vector index
↓
User asks a question
↓
FAISS retrieves top 5 most relevant chunks
↓
LangChain formats prompt with context + chat history
↓
Groq LLM (llama-3.1-8b-instant) generates grounded answer
↓
Answer + page citations returned to frontend

### Session Management

Each uploaded PDF gets a unique UUID session. The vectorstore and conversation memory are stored in a Python dictionary keyed by session ID, allowing multiple users to use the app simultaneously without interfering with each other. Sessions live in memory and are cleared when the server restarts.

### Clinical Guardrails

The system prompt explicitly instructs the model to answer only from the provided context, never hallucinate missing information, avoid medical advice or diagnosis, and always cite source page numbers. This makes the tool safe for reference use in clinical settings.

---

## 📌 Assumptions Made

| Area | Assumption |
|---|---|
| **File type** | Only PDF files are supported. Other formats (Word, images) are not handled. |
| **Language** | Documents and queries are assumed to be in English. |
| **Session persistence** | Sessions are in-memory only. Restarting the server clears all sessions and uploaded documents. |
| **Document size** | Very large PDFs (100+ pages) may take longer to process due to embedding generation. |
| **Medical use** | This tool is intended for reference only — not for clinical decision making. |
| **Embeddings** | `all-MiniLM-L6-v2` is used for its small size (~90MB) and good performance on English text. |
| **Chunk size** | 500 characters with 50 overlap — tuned for clinical documents with dense information. |

---

## 🚀 Deployment

Deployed on **Hugging Face Spaces** using Docker. The React frontend is built and served as static files by FastAPI, so everything runs as a single container on one port.

To redeploy after backend changes:

```bash
git add .
git commit -m "update"
git push space main
```

To redeploy after frontend changes:

```bash
cd frontend
npm run build:hf
cd ..
git add .
git commit -m "rebuild frontend"
git push space main
```

---

## 🔒 Environment Variables

| Variable | Where to get it | Required |
|---|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | Yes |

Never commit your `.env` file. It is listed in `.gitignore`.

---


Save as README.md at the root of your project, then:
bashgit add README.md
git commit -m "docs: add README"
git push origin main
git push space main
