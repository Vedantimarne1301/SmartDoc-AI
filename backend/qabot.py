import os
import warnings
from langchain_groq import ChatGroq
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate

warnings.filterwarnings("ignore")

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


class SimpleMemory:
    def __init__(self):
        self.messages = []

    def load_memory(self):
        if not self.messages:
            return ""
        return "\n".join([
            f"User: {m['question']}\nBot: {m['answer']}"
            for m in self.messages
        ])

    def save_context(self, question, answer):
        self.messages.append({"question": question, "answer": answer})

    def clear(self):
        self.messages = []


def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        api_key=os.environ.get("GROQ_API_KEY", "")
    )


def process_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    embeddings = FastEmbedEmbeddings()
    vectorstore = Chroma.from_documents(chunks, embedding=embeddings)
    return vectorstore


def answer_query(vectorstore, query: str, memory: SimpleMemory, top_k: int = 5):
    retrieved_docs = vectorstore.similarity_search(query, k=top_k)

    if not retrieved_docs:
        return "No relevant information found in the document.", []

    context_blocks = []
    sources = []

    for doc in retrieved_docs:
        context_blocks.append(doc.page_content)
        page = doc.metadata.get("page", "N/A")
        sources.append(f"Page {page + 1}" if isinstance(page, int) else f"Page {page}")

    context = "\n\n".join(context_blocks)
    chat_history = memory.load_memory()

    final_prompt = prompt_template.format(
        context=context,
        chat_history=chat_history,
        question=query
    )

    llm = get_llm()
    response = llm.invoke(final_prompt)
    answer = response.content if hasattr(response, "content") else str(response)

    memory.save_context(question=query, answer=answer)

    unique_sources = list(set(sources))
    return answer, unique_sources