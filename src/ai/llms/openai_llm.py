# Import base LLM class from the correct path
from .base import BaseLLM
import logging
from utils.logging import setup_logger
import time
from typing import Dict, Any, Tuple
import openai
from config.settings import get_settings
logger = setup_logger("app.llm")  # Component-level logger


class OpenAILLM(BaseLLM):
    """
    LLM wrapper for OpenAI GPT models with detailed logging.
    The default model is gpt-4.1-mini, but can be overridden via environment variable.
    """

    def __init__(self, model: str):
        settings = get_settings()
        self.model = model or settings.OPENAI_MODEL
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)  # single client for reuse

    async def generate(self, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        start_time = time.time()

        # --- Step 1: Log start of call (with prompt preview)
        logger.debug({
            "event": "llm_generate_start",
            "model": self.model,
            "prompt_preview": prompt[:100],  # Limit for privacy
            "parameters": kwargs
        })

        try:
            # --- Step 2: Perform request
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )

            # --- Step 3: Extract results
            response_text = resp.choices[0].message.content.strip()
            tokens_used = resp.usage.total_tokens
            finish_reason = resp.choices[0].finish_reason
            latency = round(time.time() - start_time, 3)
            meta = {
                "model": self.model,
                "tokens_used": tokens_used,
                "finish_reason": finish_reason,
                "latency_sec": latency,
            }

            # --- Step 4: Log success info
            logger.info({
                "event": "llm_generate_success",
                "model": self.model,
                "latency_sec": latency,
                "tokens_used": meta["tokens_used"],
                "finish_reason": meta["finish_reason"]
            })

            # --- Step 5: Log response preview at debug level
            logger.debug({
                "event": "llm_response_preview",
                "response_preview": response_text[:200]  # Avoid dumping long text
            })

            return response_text, meta

        except Exception as e:
            # --- Step 6: Log and re-raise errors
            logger.error({
                "event": "llm_generate_error",
                "model": self.model,
                "error": str(e)
            })
            raise


    async def stream(self, prompt: str, **kwargs):
        """Streams responses token by token with logging."""
        logger.debug({
            "event": "llm_stream_start",
            "model": self.model,
            "prompt_preview": prompt[:80]
        })

        try:
            async_client = openai.AsyncOpenAI()
            stream = await async_client.responses.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                **kwargs,
            )

            async for event in stream:
                yield event

            logger.info({
                "event": "llm_stream_complete",
                "model": self.model
            })

        except Exception as e:
            logger.exception({
                "event": "llm_stream_error",
                "model": self.model,
                "error": str(e)
            })
            raise


    async def get_model_info(self) -> Dict[str, Any]:
        """Returns LLM provider and model info."""
        logger.debug({
            "event": "get_model_info",
            "model": self.model
        })
        return {"provider": "openai", "model": self.model}
