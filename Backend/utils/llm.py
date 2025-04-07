from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


client = OpenAI(api_key=os.getenv("DEEP_SEEK_KEY"), base_url="https://api.deepseek.com")


def ask_llm(system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()
