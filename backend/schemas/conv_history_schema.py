from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4


class ConversationEntry(BaseModel):
    """A single turn in a conversation.

    Rationale for fields:
    - id: unique id for this record (helps de-duplication and references)
    - conversation_id: groups entries into a session or conversation
    - user_id: who initiated the message (can be anonymous or internal id)
    - role: who authored the message (user/system/assistant) for accurate playback
    - message / response: the user text and assistant reply (assistant may be blank for user-only logs)
    - model: which model produced the response (useful for debugging/repro repro)
    - tokens_used / latency_ms: lightweight telemetry for cost & perf tracking
    - feedback_rating / feedback_comment: optional user signal for improvement
    - messasge_metadata: arbitrary key/value useful to store source, channel, intent, etc.
    - attachments: optional list of attachment ids/urls (audio, images)
    - timestamp: when the entry was created
    """

    id: UUID = Field(default_factory=uuid4, description="Unique id for this entry")
    # conversation_id: Optional[UUID] = Field(None, description="ID grouping related entries / session")
    user_id: Optional[str] = Field(None, description="Identifier for the user (if available)")
    role: str = Field("user", description="Role of the author: user | assistant | system")
    message: str
    # response: Optional[str] = Field(None, description="Assistant response; may be empty for user-only logs")
    model: Optional[str] = Field(None, description="Model name/version used to produce `response`")
    tokens_used: Optional[int] = Field(None, description="Approx tokens used for this turn")
    latency_ms: Optional[float] = Field(None, description="Response latency in milliseconds")
    feedback_rating: Optional[int] = Field(None, ge=1, le=5, description="Optional user rating 1-5")
    feedback_comment: Optional[str] = Field(None, description="Optional free-text feedback")
    messasge_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Arbitrary metadata (source, intent, channel, etc.)")
    attachments: Optional[List[str]] = Field(None, description="Optional list of attachment URLs or IDs")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp for this entry")


class ConversationHistoryRequest(BaseModel):
    """Request schema for fetching conversation history."""
    user_id: str = Field(..., description="Identifier for the user whose history is requested")
    limit: Optional[int] = Field(10, description="Maximum number of entries to return")

class ConversationHistoryResponse(BaseModel):
    """Response schema for conversation history."""
    user_id: str = Field(..., description="Identifier for the user whose history is returned")
    history: List[ConversationEntry] = Field(..., description="List of conversation entries")