from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agents.manager_agent import ManagerAgent
from utils.rag import load_pdf_chunks, build_vector_index
from fastapi.responses import StreamingResponse
import asyncio

# Preload RAG vector DB once
chunks = load_pdf_chunks("agents/data/partsdata.pdf")
print(f"✅ Loaded {len(chunks)} PDF chunks.")

index, _, _ = build_vector_index(chunks)
print("✅ FAISS index built with", index.ntotal, "vectors.")


# Initialize manager with shared RAG data
manager = ManagerAgent(chunks, index)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_stream(request: Request):
    body = await request.json()
    message = body.get("message", "")
    history = body.get("history", [])

    async def generate():
        async for token in manager.stream(message, history):
            yield token

    return StreamingResponse(generate(), media_type="text/plain")