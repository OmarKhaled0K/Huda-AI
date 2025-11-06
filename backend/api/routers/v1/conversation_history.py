from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.db import get_db
from services.conv_service import ConversationService
from schemas.conv_history_schema import (
    ConversationEntry,
    ConversationHistoryRequest,
    ConversationHistoryResponse,
)

conversation_history_router = APIRouter(
    prefix="/conversation-history",
    tags=["Conversation History"]
)

@conversation_history_router.post("/messages/", response_model=ConversationEntry)
async def create_message(
    message: ConversationEntry,
    db: Session = Depends(get_db)
) -> ConversationEntry:
    """Create a new message entry."""
    conv_service = ConversationService(db)
    db_message = conv_service.create_message(message)
    return db_message

@conversation_history_router.get("/messages/{message_id}", response_model=ConversationEntry)
async def get_message(
    message_id: str,
    db: Session = Depends(get_db)
) -> ConversationEntry:
    """Retrieve a specific message by ID."""
    conv_service = ConversationService(db)
    message = conv_service.get_message(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message.to_dict()

@conversation_history_router.put("/messages/{message_id}", response_model=ConversationEntry)
async def update_message(
    message_id: str,
    update_data: dict,
    db: Session = Depends(get_db)
) -> ConversationEntry:
    """
    Update a message.
    message schema:
            {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "user_id": "string",
        "role": "user",
        "message": "string",
        "model": "string",
        "tokens_used": 0,
        "latency_ms": 0,
        "feedback_rating": 1,
        "feedback_comment": "string",
        "metadata": {
            "additionalProp1": {}
        },
        "attachments": [
            "string"
        ],
        "timestamp": "2025-11-06T22:19:40.809Z"
        }
    """
    conv_service = ConversationService(db)
    print(f"Conversation service")
    updated_message = conv_service.update_message(message_id, update_data)
    if not updated_message:
        raise HTTPException(status_code=404, detail="Message not found")
    print(f"Updated message: {update_data}")
    return updated_message

@conversation_history_router.delete("/messages/{message_id}")
async def delete_message(
    message_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """Delete a message."""
    conv_service = ConversationService(db)
    deleted_message = conv_service.delete_message(message_id)
    if not deleted_message:
        raise HTTPException(status_code=404, detail="Message not found")
    return deleted_message.to_dict()

@conversation_history_router.get("/history/", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    request: ConversationHistoryRequest = Depends(),
    db: Session = Depends(get_db)
) -> ConversationHistoryResponse:
    """Retrieve conversation history for a user."""
    conv_service = ConversationService(db)
    return conv_service.get_conversation_history(request.user_id, request.limit)

@conversation_history_router.get("/{conversation_id}", response_model=List[ConversationEntry])
async def get_conversation_by_id(
    conversation_id: str,
    db: Session = Depends(get_db)
) -> List[ConversationEntry]:
    """Retrieve all messages in a conversation."""
    conv_service = ConversationService(db)
    messages = conv_service.get_conversation_by_id(conversation_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return [ConversationEntry.model_validate(msg) for msg in messages]

@conversation_history_router.put("/messages/{message_id}/feedback", response_model=ConversationEntry)
async def update_message_feedback(
    message_id: str,
    rating: Optional[int] = Query(None, ge=1, le=5),
    comment: Optional[str] = None,
    db: Session = Depends(get_db)
) -> ConversationEntry:
    """Update feedback for a message."""
    conv_service = ConversationService(db)
    updated_message = conv_service.update_message_feedback(message_id, rating, comment)
    if not updated_message:
        raise HTTPException(status_code=404, detail="Message not found")
    return ConversationEntry.model_validate(updated_message)