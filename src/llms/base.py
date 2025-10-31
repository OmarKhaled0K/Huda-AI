from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseLLM(ABC):
    """Abstract base class that defines a unified interface for all LLMs."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model."""
        pass

    @abstractmethod
    async def stream(self, prompt: str, **kwargs):
        """Optional streaming interface."""
        pass

    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        """Return info about the active model (for debugging)."""
        pass
