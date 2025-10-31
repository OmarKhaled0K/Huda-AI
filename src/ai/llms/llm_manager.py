# app/llms/llm_manager.py
import os
from .openai_llm import OpenAILLM
from .llama_llm import LlamaLLM
from .deepseek_llm import DeepSeekLLM
from .base import BaseLLM


def get_llm() -> BaseLLM:
    """Factory that returns the appropriate LLM instance."""
    provider = os.getenv("LLM_PROVIDER", "openai").lower()

    if provider == "openai":
        return OpenAILLM( model=os.getenv("OPENAI_MODEL", "gpt-4.1"))

    elif provider == "llama":
        return LlamaLLM(model=os.getenv("LLAMA_MODEL", "llama-3.1"))

    elif provider == "deepseek":
        return DeepSeekLLM(api_key=os.getenv("DEEPSEEK_API_KEY"), model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"))

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
