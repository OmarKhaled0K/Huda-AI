from fastapi import APIRouter, HTTPException
from schemas import ChatRequest, ChatResponse
from ai.llms.llm_manager import get_llm
import logging

basic_chat_router = APIRouter(prefix="/chat", tags=["Basic Chat"])
logger = logging.getLogger(__name__)

@basic_chat_router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Basic chat endpoint that sends a prompt to the LLM and returns the response.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    try:
        llm = get_llm()
        llm_kwargs = {k: v for k, v in request.model_dump().items() if v is not None and k != "message"}
        response_text, meta = await llm.generate(request.message, **llm_kwargs)
        logger.info(f"Chat completed using model={meta.get('model')}")

        return ChatResponse(
            response=response_text,
            model=meta.get("model"),
            tokens_used=meta.get("tokens_used"),
        )

    except Exception as e:
        logger.exception("Error in chat_endpoint")
        raise HTTPException(status_code=500, detail=str(e))
