from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from datetime import datetime, timezone
from uuid import uuid4
from .base import Base

class MessageModel(Base):
    __tablename__ = 'conversation_history'

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    # conversation_id = Column(String, ForeignKey('conversations.id'), nullable=True)
    user_id = Column(String, nullable=True)
    role = Column(String, nullable=False, default='user')
    message = Column(String, nullable=False)
    # response = Column(String, nullable=True)
    model = Column(String, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    feedback_rating = Column(Integer, nullable=True)
    feedback_comment = Column(String, nullable=True)
    messasge_metadata = Column(String, nullable=True)  # Consider using JSON type if supported
    attachments = Column(String, nullable=True)  # Consider using JSON type if supported
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Index to retrieve messages by conversation_id and another to retrieve by user_id
    __table_args__ = (
        Index('idx_conversation_id', 'id'),
        Index('idx_user_id', 'user_id'),
    )
    def __repr__(self):
        return f"<MessageModel(id={self.id}, role={self.role}, timestamp={self.timestamp})>"
        
    def to_dict(self) -> dict:
        """Convert the model instance to a dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role": self.role,
            "message": self.message,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "feedback_rating": self.feedback_rating,
            "feedback_comment": self.feedback_comment,
            "messasge_metadata": eval(self.messasge_metadata) if self.messasge_metadata else None,
            "attachments": eval(self.attachments) if self.attachments else None,
            "timestamp": self.timestamp
        }