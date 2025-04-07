import fitz  # PyMuPDF
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai_embed_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  
def embed(text: str):
    response = openai_embed_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.array(response.data[0].embedding)

def load_pdf_chunks(pdf_path: str) -> list:
    doc = fitz.open(pdf_path)
    chunks = []
    for page in doc:
        text = page.get_text().strip()
        if text:
            for para in text.split("\n\n"):
                para = para.strip()
                if para:
                    chunks.append(para)
    return chunks

def build_vector_index(chunks: list):
    embeddings = [embed(chunk) for chunk in chunks]
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype('float32'))
    return index, embeddings, chunks

def retrieve(query: str, index, chunks: list, k: int = 3):
    q_vec = embed(query).astype('float32').reshape(1, -1)
    distances, indices = index.search(q_vec, k)
    print("🔍 RAG distances:", distances)
    print("🧠 RAG indices:", indices)
    return [chunks[i] for i in indices[0] if i < len(chunks)]

