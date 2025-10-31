from fastapi import APIRouter, HTTPException
from llms.llm_manager import get_llm
router = APIRouter(tags=["Basic Chat"])

@router.post("/chat")
async def chat_endpoint(message: str):
    """A basic chat endpoint that echoes the received message."""
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    llm = get_llm()
    response = await llm.generate(message)
    return {"response": response}