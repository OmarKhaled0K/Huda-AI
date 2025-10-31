from .base import BaseLLM
from typing import Dict, Any
import asyncio


class LlamaLLM(BaseLLM):
    """Mock implementation of a Llama model (replace with actual API call)."""

    def __init__(self, model: str = "llama-3.1", endpoint: str | None = None):
        self.model = model
        self.endpoint = endpoint or "http://localhost:11434"

    async def generate(self, prompt: str, **kwargs) -> str:
        # Simulate a model call
        await asyncio.sleep(0.2)
        return f"[Llama] Response to: {prompt[:50]}..."

    async def stream(self, prompt: str, **kwargs):
        for token in "[Llama] streaming simulated output...".split():
            await asyncio.sleep(0.1)
            yield token + " "

    async def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "llama", "model": self.model, "endpoint": self.endpoint}
