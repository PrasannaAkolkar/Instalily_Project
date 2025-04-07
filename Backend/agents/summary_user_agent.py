from agents.base_agent import BaseAgent
from typing import AsyncGenerator
from openai import OpenAI
import os
import asyncio

class SummarizationAgent(BaseAgent):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("DEEP_SEEK_KEY"), base_url="https://api.deepseek.com")

    def build_prompt(self, history: list[dict]) -> tuple[str, str]:
        trimmed = history[-8:]
        conversation = ""

        for msg in trimmed:
            role = msg["role"].capitalize()
            content = msg["content"][:600]
            conversation += f"{role}: {content}\n"

        system_prompt = (
            "You are a summarization assistant. Your job is to summarize the following conversation between a user and an assistant. "
            "Focus on key topics like appliance part numbers, installation help, compatibility checks, or troubleshooting.\n\n"
            "Return a helpful bullet-point summary for a manager or support engineer."
        )

        user_prompt = f"Conversation:\n{conversation.strip()}\n\nSummary (bullet points):"
        return system_prompt, user_prompt

    async def stream(self, history: list[dict]) -> AsyncGenerator[str, None]:
        print("📝 SummarizationAgent: Starting streamed summary...")

        try:
            system_prompt, user_prompt = self.build_prompt(history)

            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=True
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    yield token
                    await asyncio.sleep(0.01)

        except Exception as e:
            print("❌ Summarization stream error:", e)
            yield "⚠️ Something went wrong while generating the summary."
    
    # just for non stream

    # def run(self, history: list[dict]) -> str:
    #     # Keep this if you still want sync summary support for testing
    #     try:
    #         system_prompt, user_prompt = self.build_prompt(history)
    #         return self.client.chat.completions.create(
    #             model="deepseek-chat",
    #             messages=[
    #                 {"role": "system", "content": system_prompt},
    #                 {"role": "user", "content": user_prompt}
    #             ],
    #         ).choices[0].message.content
    #     except Exception as e:
    #         print("❌ Error in run():", e)
    #         return "⚠️ Failed to generate summary."
