from agents.base_agent import BaseAgent
from utils.rag import retrieve

class ProductAgent(BaseAgent):
    def __init__(self, chunks=None, index=None):
        self.chunks = chunks
        self.index = index

    def build_prompt(self, message: str, context: str = "") -> str:
        rag_context = ""
        if self.chunks and self.index:
            print("🔍 ProductAgent: Retrieving relevant chunks...")
            context_chunks = retrieve(message, self.index, self.chunks, k=5)
            rag_context = "\n\n".join(context_chunks)
            print("📄 Top RAG chunks retrieved:", context_chunks)


            print("📄 ProductAgent: RAG context added.")

        return (
            "You are a knowledgeable product assistant for appliance parts. "
            "Answer questions related to product descriptions, customer feedback, availability, and pricing. "
            "Use provided context from manuals, product info, or customer feedback when available.\n\n"
            f"Recent chat or user context:\n{context}\n\n"
            f"Relevant product document context:\n{rag_context}\n\n"
            f"User question: {message}"
        )
