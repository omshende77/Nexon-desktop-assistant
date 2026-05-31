from sqlalchemy.orm import Session
from ..models import Message

class MessageRepository:
    def create(self, db: Session, conversation_id: int, role: str, content: str, message_type: str = "text", user_id: int = None) -> Message:
        db_msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_type=message_type,
            user_id=user_id
        )
        db.add(db_msg)
        db.commit()
        db.refresh(db_msg)
        return db_msg

    def get_by_conversation(self, db: Session, conversation_id: int, skip: int = 0, limit: int = 1000):
        return db.query(Message).filter(Message.conversation_id == conversation_id)\
                 .order_by(Message.created_at.asc()).offset(skip).limit(limit).all()
