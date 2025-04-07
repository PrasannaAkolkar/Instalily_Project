from agents.base_agent import BaseAgent
from utils.llm import ask_llm
from utils.rag import retrieve

class InstallAgent(BaseAgent):
    def __init__(self, chunks, index):
        self.chunks = chunks
        self.index = index


    def build_prompt(self, message: str, chat_context: str) -> str:
        print("🔍 InstallAgent: Retrieving relevant chunks...")
        context_chunks = retrieve(message, self.index, self.chunks, k=2)
        context = "\n\n".join(context_chunks)

        print("📄 Context chunks added to prompt.")

        return (
            "You are an installation assistant for refrigerator and dishwasher parts. "
            "Use the recent conversation and manual context to help the user install the part step-by-step.\n\n"
            f"Recent conversation:\n{chat_context}\n\n"
            f"Relevant manual context:\n{context}\n\n"
            f"Question: {message}"
        )

    # just for non stream

    # def run(self, message: str, chat_context: str = "") -> str:
    #     print("🔍 InstallAgent: Retrieving relevant chunks...")
    #     context_chunks = retrieve(message, self.index, self.chunks, k=2)
    #     context = "\n\n".join(context_chunks)
    #     if len(context) > 3000:
    #         context = context[:3000]

    #     print("💬 InstallAgent: Sending prompt to LLM...")
    #     system_prompt = (
    #         "You are an installation assistant for refrigerator and dishwasher parts. "
    #         "Use the recent conversation and manual context to help the user install the part step-by-step."
    #     )

    #     user_prompt = (
    #         f"Recent conversation:\n{chat_context}\n\n"
    #         f"Relevant manual context:\n{context}\n\n"
    #         f"Question: {message}"
    #     )

    #     response = ask_llm(system_prompt, user_prompt)
    #     print("✅ InstallAgent: Response received.")
    #     return response
