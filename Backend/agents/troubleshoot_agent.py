from agents.base_agent import BaseAgent
from utils.llm import ask_llm
from utils.rag import retrieve

class TroubleshootAgent(BaseAgent):
    def __init__(self, chunks, index):
        self.chunks = chunks
        self.index = index
    
    def build_prompt(self, message: str, context: str) -> str:
        print("🔍 TroubleshootAgent: Retrieving relevant chunks...")
        context_chunks = retrieve(message, self.index, self.chunks, k=2)
        rag_context = "\n\n".join(context_chunks)

        print("📄 TroubleshootAgent: Context injected into prompt.")

        return (
            "You are an appliance repair expert. "
            "Use the context from the product manual to diagnose and suggest helpful fixes for the user's issue.\n\n"
            f"Recent conversation:\n{context}\n\n"
            f"Relevant manual context:\n{rag_context}\n\n"
            f"Problem: {message}"
        )

    # just for non stream

    # def run(self, message: str, chat_context: str = "") -> str:
    #     print("🔍 TroubleshootAgent: Retrieving relevant chunks...")
    #     context_chunks = retrieve(message, self.index, self.chunks, k=2)
    #     context = "\n\n".join(context_chunks)
    #     if len(context) > 3000:
    #         context = context[:3000]

    #     print("💬 TroubleshootAgent: Sending prompt to LLM...")
    #     system_prompt = (
    #         "You are a troubleshooting assistant for appliance parts. "
    #         "Use recent conversation and manual data to suggest steps to diagnose or fix the issue."
    #     )

    #     user_prompt = (
    #         f"Recent conversation:\n{chat_context}\n\n"
    #         f"Relevant manual context:\n{context}\n\n"
    #         f"Problem: {message}"
    #     )

    #     response = ask_llm(system_prompt, user_prompt)
    #     print("✅ TroubleshootAgent: Response received.")
    #     return response
