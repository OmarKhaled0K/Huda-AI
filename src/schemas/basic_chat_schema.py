from pydantic import BaseModel, Field
from typing import Optional

class ChatRequest(BaseModel):
    message: str = Field(..., example="Hello, Huda!")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Controls randomness")
    max_tokens: Optional[int] = Field(256, ge=1, le=2048, description="Response length limit")

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: Optional[int] = None
