# app/llms/llm_manager.py
import os
from .openai_llm import OpenAILLM
from .llama_llm import LlamaLLM
from .deepseek_llm import DeepSeekLLM
from .base import BaseLLM
from config.settings import get_settings


def get_llm() -> BaseLLM:
    settings = get_settings()
    """Factory that returns the appropriate LLM instance."""
    provider = settings.LLM_PROVIDER.lower()

    if provider == "openai":
        return OpenAILLM( model=settings.OPENAI_MODEL )

    elif provider == "llama":
        return LlamaLLM(model=settings.LLAMA_MODEL)


    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
