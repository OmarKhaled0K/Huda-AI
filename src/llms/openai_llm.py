# Import base LLM class from the correct path
from .base import BaseLLM
from typing import Dict, Any
import os
import openai
from dotenv import load_dotenv

class OpenAILLM(BaseLLM):
    """LLM wrapper for OpenAI GPT models."""

    def __init__(self, model: str = "gpt-4.1"):
        self.model = model
        load_dotenv()

    async def generate(self, prompt: str, **kwargs) -> str:
        resp = openai.OpenAI().chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return resp.choices[0].message.content.strip()
    


    async def stream(self, prompt: str, **kwargs):
        stream = await openai.AsyncOpenAI().responses.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            **kwargs,
        )
        async for event in stream:
                yield event

    async def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "openai", "model": self.model}
