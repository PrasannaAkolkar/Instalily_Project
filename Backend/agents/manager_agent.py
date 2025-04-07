from agents.install_agent import InstallAgent
from agents.compatibility_agent import CompatibilityAgent
from agents.troubleshoot_agent import TroubleshootAgent
from agents.summary_user_agent import SummarizationAgent
from agents.product_agent import ProductAgent
from agents.order_tracking_agent import OrderTrackingAgent
from utils.llm import ask_llm
from functools import lru_cache
import re
import asyncio
from openai import OpenAI
import os
import asyncio
from typing import AsyncGenerator


class ManagerAgent:
    def __init__(self, chunks, index):
        self.install_agent = InstallAgent(chunks, index)
        self.compatibility_agent = CompatibilityAgent(chunks, index)
        self.troubleshoot_agent = TroubleshootAgent(chunks, index)
        self.summarization_agent = SummarizationAgent()
        self.last_part_number = None
        self.product_agent = ProductAgent(chunks, index)
        self.order_tracking_agent = OrderTrackingAgent()
        self.client = OpenAI(api_key=os.getenv("DEEP_SEEK_KEY"), base_url="https://api.deepseek.com")


    @lru_cache(maxsize=512)
    def classify_intent(self, message: str) -> str:
        print("🧠 Classifying intent...")
        system_prompt = (
            "You are a helpful assistant that classifies user messages into one of six categories: "
            "'install', 'compatibility', 'troubleshoot','product', 'order-status' or summary-user-conversation.\n"
            "Only respond with one of these words.\n"
            "Do not include explanations.\n"
            "If the message is unrelated to appliance parts, return 'off-topic'."
        )
        user_prompt = f"Message: \"{message}\"\n\nCategory:"
        intent = ask_llm(system_prompt, user_prompt).strip().lower()
        print(f"✅ Intent classified as: {intent}")
        return intent

    def extract_part_number(self, message: str) -> str | None:
        match = re.search(r"PS\d+", message.upper())
        if match:
            return match.group()
        return None
    
    # just for non stream
    
    # def run(self, message: str, history: list[dict]) -> str:
    #     print("📩 New message received:", message)

    #     # Extract part number from current or remembered message
    #     part_number = self.extract_part_number(message)
    #     if part_number:
    #         self.last_part_number = part_number
    #     elif any(p in message.lower() for p in ["this part", "it", "that part"]) and self.last_part_number:
    #         for phrase in ["this part", "it", "that part"]:
    #             message = message.replace(phrase, self.last_part_number)
    #     elif not self.last_part_number and "this part" in message.lower():
    #         return "Please mention the part number so I can help you better."

    #     # 🧠 Add memory-based context to the prompt
    #     chat_context = ""
    #     for msg in history[-4:]:  # use last 4 messages
    #         role = msg["role"]
    #         content = msg["content"]
    #         chat_context += f"{role.capitalize()}: {content}\n"

    #     print("📚 Recent history being used:\n", chat_context)

    #     # Determine intent
    #     intent = self.classify_intent(message)

    #     # Route to the appropriate agent
    #     if intent == "install":
    #         return self.install_agent.run(message, chat_context)
    #     elif intent == "compatibility":
    #         return self.compatibility_agent.run(message, chat_context)
    #     elif intent == "troubleshoot":
    #         return self.troubleshoot_agent.run(message, chat_context)
    #     elif intent == "summary-user-conversation":
    #         return self.summarization_agent.run(history)
    #     else:
    #         return (
    #             "I'm here to help with appliance part-related questions, such as:\n"
    #             "- Installation guidance (e.g., 'How to install PS11752778?')\n"
    #             "- Compatibility with your model (e.g., 'Does this work with WDT780SAEM1?')\n"
    #             "- Troubleshooting common part issues (e.g., 'Ice maker not working')"
    #         )



    async def stream(self, message: str, history: list[dict]) -> AsyncGenerator[str, None]:
        print("📩 Streaming mode activated.")

       
        part_number = self.extract_part_number(message)
        if part_number:
            self.last_part_number = part_number
        elif any(p in message.lower() for p in ["this part", "it", "that part"]) and self.last_part_number:
            for phrase in ["this part", "it", "that part"]:
                message = message.replace(phrase, self.last_part_number)
        elif not self.last_part_number and "this part" in message.lower():
            yield "Please mention the part number so I can help you better."
            return

        chat_context = ""
        for msg in history[-4:]:
            chat_context += f"{msg['role'].capitalize()}: {msg['content']}\n"
        print("📚 Recent history:\n", chat_context)

        intent = self.classify_intent(message)
        print(f"🧠 Intent = {intent}")

        if intent == "install":
            prompt = self.install_agent.build_prompt(message, chat_context)
        elif intent == "compatibility":
            prompt = self.compatibility_agent.build_prompt(message, chat_context)
        elif intent == "troubleshoot":
            prompt = self.troubleshoot_agent.build_prompt(message, chat_context)
        elif intent == "product":
            prompt = self.product_agent.build_prompt(message, chat_context)
        elif intent == "order-status":
            final_message = self.order_tracking_agent.build_prompt(message, chat_context)
            yield final_message
            return 
            # prompt = self.order_tracking_agent.build_prompt(message, chat_context)
        elif intent == "summary-user-conversation":
            print("📝 Delegating to SummarizationAgent.stream()")
            async for chunk in self.summarization_agent.stream(history):
                yield chunk
            return
        else:
            yield (
                "I'm here to help with appliance part-related questions, such as:\n"
                "- Installation guidance (e.g., 'How to install PS11752778?')\n"
                "- Compatibility with your model (e.g., 'Does this work with WDT780SAEM1?')\n"
                "- Troubleshooting common part issues (e.g., 'Ice maker not working')"
            )
            return

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": prompt}],
            stream=True
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                # print("🧩 Token:", token)
                yield token
                await asyncio.sleep(0.01)

