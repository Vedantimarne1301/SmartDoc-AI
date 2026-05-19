import os
import uuid
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from qabot import process_pdf, answer_query, SimpleMemory
from dotenv import load_dotenv
import tempfile

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions: dict = {}


class QueryRequest(BaseModel):
    session_id: str
    question: str


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    session_id = str(uuid.uuid4())
    temp_path = os.path.join(tempfile.gettempdir(), f"{session_id}.pdf")

    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        vectorstore = process_pdf(temp_path)
        sessions[session_id] = {
            "vectorstore": vectorstore,
            "memory": SimpleMemory(),
            "filename": file.filename,
        }
        return {
            "session_id": session_id,
            "filename": file.filename,
            "message": "PDF processed successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/api/query")
async def query(request: QueryRequest):
    session = sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a PDF first.")

    try:
        answer, sources = answer_query(
            vectorstore=session["vectorstore"],
            query=request.question,
            memory=session["memory"]
        )
        return {
            "answer": answer,
            "sources": sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
    return {"message": "Session cleared"}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Serve React frontend in production
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")