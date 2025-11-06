from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID

from models.message_model import MessageModel
from schemas.conv_history_schema import ConversationEntry, ConversationHistoryResponse

class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def create_message(self, message: ConversationEntry) -> MessageModel:
        """Create a new message entry in the database."""
        db_message = MessageModel(
            id=str(message.id),
            # conversation_id=str(message.conversation_id) if message.conversation_id else None,
            user_id=message.user_id,
            role=message.role,
            message=message.message,
            # response=message.response,
            model=message.model,
            tokens_used=message.tokens_used,
            latency_ms=message.latency_ms,
            feedback_rating=message.feedback_rating,
            feedback_comment=message.feedback_comment,
            metadata=str(message.metadata) if message.metadata else None,
            attachments=str(message.attachments) if message.attachments else None,
        )
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        return db_message.to_dict()

    def get_message(self, message_id: str) -> Optional[MessageModel]:
        """Retrieve a specific message by its ID."""
        message = self.db.query(MessageModel).filter(MessageModel.id == message_id).first()
        return message

    def update_message(self, message_id: str, update_data: dict) -> Optional[dict]:
        """Update a message with new data."""
        message = self.get_message(message_id)
        if not message:
            return None
            
        # Update only valid fields
        valid_fields = [
            'user_id', 'role', 'message', 'response', 'model',
            'tokens_used', 'latency_ms', 'feedback_rating',
            'feedback_comment', 'metadata', 'attachments'
        ]
        
        for field, value in update_data.items():
            if field in valid_fields and hasattr(message, field):
                # Handle special cases for metadata and attachments
                if field in ['metadata', 'attachments'] and value is not None:
                    value = str(value)
                setattr(message, field, value)
                
        try:
            self.db.commit()
            self.db.refresh(message)
            return message.to_dict()
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to update message: {str(e)}")

    def delete_message(self, message_id: str) -> bool:
        """Delete a message by its ID."""
        message = self.get_message(message_id)
        if message:
            self.db.delete(message)
            self.db.commit()
            return message
        return False

    def get_conversation_history(self, user_id: str, limit: int = 10) -> ConversationHistoryResponse:
        """Retrieve conversation history for a user."""
        messages = (
            self.db.query(MessageModel)
            .filter(MessageModel.user_id == user_id)
            .order_by(desc(MessageModel.timestamp))
            .limit(limit)
            .all()
        )
        
        history = [
            ConversationEntry(
                id=UUID(message.id),
                # conversation_id=UUID(message.conversation_id) if message.conversation_id else None,
                user_id=message.user_id,
                role=message.role,
                message=message.message,
                model=message.model,
                tokens_used=message.tokens_used,
                latency_ms=message.latency_ms,
                feedback_rating=message.feedback_rating,
                feedback_comment=message.feedback_comment,
                messasge_metadata=message.messasge_metadata if message.messasge_metadata else {},
                attachments=message.attachments if message.attachments else None,
                timestamp=message.timestamp
            )
            for message in messages
        ]
        
        return ConversationHistoryResponse(user_id=user_id, history=history)

    def get_conversation_by_id(self, id: str) -> List[MessageModel]:
        """Retrieve all messages in a specific conversation."""
        return (
            self.db.query(MessageModel)
            .filter(MessageModel.id == id)
            .order_by(MessageModel.timestamp)
            .all()
        )

    def update_message_feedback(
        self, message_id: str, rating: Optional[int] = None, comment: Optional[str] = None
    ) -> Optional[dict]:
        """Update feedback for a specific message."""
        update_data = {}
        if rating is not None:
            update_data["feedback_rating"] = rating
        if comment is not None:
            update_data["feedback_comment"] = comment
        
        return self.update_message(message_id, update_data)
