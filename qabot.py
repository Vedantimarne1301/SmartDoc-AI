import os
import warnings
import gradio as gr

from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate

warnings.filterwarnings("ignore")

# ------------------ LLM (Groq) ------------------
def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        api_key=os.environ.get("GROQ_API_KEY", "")
    )

# ------------------ System Prompt ------------------
SYSTEM_PROMPT = """
You are a clinical document intelligence assistant designed to help healthcare
professionals quickly retrieve and summarize information from uploaded patient records.

Rules:
- Answer ONLY using the provided context.
- Do NOT provide medical advice, diagnosis, or treatment recommendations.
- Do NOT hallucinate or infer missing information.
- If information is not present, clearly say it is unavailable.
- Keep responses concise, factual, and clinically relevant.
- Cite sources using page numbers.
"""

# ------------------ Prompt Template ------------------
prompt_template = PromptTemplate(
    input_variables=["context", "chat_history", "question"],
    template="""
{system_prompt}

Chat History:
{chat_history}

Context:
{context}

User Question:
{question}

Answer (based only on the context above, include citations):
""",
    partial_variables={"system_prompt": SYSTEM_PROMPT}
)

# ------------------ Simple Conversation Memory ------------------
class SimpleMemory:
    def __init__(self):
        self.messages = []

    def load_memory(self):
        """Return chat history as formatted string"""
        if not self.messages:
            return ""
        return "\n".join([f"User: {m['question']}\nBot: {m['answer']}" 
                          for m in self.messages])

    def save_context(self, question, answer):
        """Save a single Q&A"""
        self.messages.append({"question": question, "answer": answer})


# Initialize memory
memory = SimpleMemory()

# ------------------ Document Processing ------------------
def load_documents(file_path):
    loader = PyPDFLoader(file_path)
    return loader.load()

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_documents(documents)

def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def build_vectorstore(chunks):
    embeddings = get_embeddings()
    return Chroma.from_documents(chunks, embedding=embeddings)

# ------------------ RAG Logic ------------------
def rag_qa(file_path, query, top_k=5):
    # Load & split documents
    documents = load_documents(file_path)
    chunks = split_documents(documents)

    if not chunks:
        return "No text found in the PDF."

    # Build vector store
    vectorstore = build_vectorstore(chunks)

    # Retrieve relevant chunks
    retrieved_docs = vectorstore.similarity_search(query, k=top_k)

    if not retrieved_docs:
        return "No relevant information found in the document."

    # Build context + sources
    context_blocks = []
    sources = []

    for doc in retrieved_docs:
        context_blocks.append(doc.page_content)
        page = doc.metadata.get("page", "N/A")
        sources.append(f"Page {page + 1 if isinstance(page, int) else page}")

    context = "\n\n".join(context_blocks)

    # Load chat history
    chat_history = memory.load_memory()

    # Format prompt
    final_prompt = prompt_template.format(
        context=context,
        chat_history=chat_history,
        question=query
    )

    # Call LLM
    llm = get_llm()
    response = llm.invoke(final_prompt)
    answer = response.content if hasattr(response, "content") else str(response)

    # Save conversation to memory
    memory.save_context(question=query, answer=answer)

    # Append citations
    unique_sources = list(set(sources))
    citation_text = "\n\nSources:\n" + "\n".join(unique_sources)

    return answer + citation_text

# ------------------ Gradio UI ------------------
rag_app = gr.Interface(
    fn=rag_qa,
    inputs=[
        gr.File(label="Upload PDF file", file_types=[".pdf"], type="filepath"),
        gr.Textbox(label="Input Query", lines=2, placeholder="Ask about the document")
    ],
    outputs=gr.Textbox(label="Answer"),
    title="SmartDoc – Clinical Document Intelligence",
    description="Upload patient records and ask clinical questions. Responses are document-grounded with source citations."
)

if __name__ == "__main__":
    rag_app.launch(server_name="127.0.0.1", server_port=3000)
