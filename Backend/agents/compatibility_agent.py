from agents.base_agent import BaseAgent
from utils.llm import ask_llm
from utils.rag import retrieve

class CompatibilityAgent(BaseAgent):
    def __init__(self, chunks, index):
        self.chunks = chunks
        self.index = index

    def build_prompt(self, message: str, context: str) -> str:
        print("🔍 CompatibilityAgent: Retrieving relevant chunks...")
        context_chunks = retrieve(message, self.index, self.chunks, k=4)
        rag_context = "\n\n".join(context_chunks)

        print("📄 CompatibilityAgent: Context injected into prompt.")

        return (
            "You are an appliance compatibility expert. "
            "Given the user's question and the manual context, determine whether the mentioned part works with the specified model. "
            "Answer clearly and helpfully.\n\n"
            f"Recent conversation:\n{context}\n\n"
            f"Relevant manual context:\n{rag_context}\n\n"
            f"Question: {message}"
        )

    # just for non stream
    # def run(self, message: str, chat_context: str = "") -> str:
    #     print("🔍 CompatibilityAgent: Retrieving relevant chunks...")
    #     context_chunks = retrieve(message, self.index, self.chunks, k=2)
    #     context = "\n\n".join(context_chunks)
    #     if len(context) > 3000:
    #         context = context[:3000]

    #     print("💬 CompatibilityAgent: Sending prompt to LLM...")
    #     system_prompt = (
    #         "You are a compatibility expert for refrigerator and dishwasher parts. "
    #         "Use the product manual and recent chat to determine if the part fits the given model."
    #     )

    #     user_prompt = (
    #         f"Recent conversation:\n{chat_context}\n\n"
    #         f"Relevant manual context:\n{context}\n\n"
    #         f"Question: {message}"
    #     )

    #     response = ask_llm(system_prompt, user_prompt)
    #     print("✅ CompatibilityAgent: Response received.")
    #     return response
