# app/llms/deepseek_llm.py
from .base import BaseLLM
from typing import Dict, Any
import asyncio


class DeepSeekLLM(BaseLLM):
    """Simplified DeepSeek wrapper. Replace with real client integration."""

    def __init__(self, api_key: str | None = None, model: str = "deepseek-chat"):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, **kwargs) -> str:
        # Simulate latency
        await asyncio.sleep(0.3)
        return f"[DeepSeek] Answer to: {prompt[:50]}..."

    async def stream(self, prompt: str, **kwargs):
        for token in "[DeepSeek] streaming simulated output...".split():
            await asyncio.sleep(0.1)
            yield token + " "

    async def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "deepseek", "model": self.model}
