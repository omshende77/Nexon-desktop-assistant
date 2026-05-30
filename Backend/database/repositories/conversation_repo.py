from sqlalchemy.orm import Session
from ..models import Conversation

class ConversationRepository:
    def create(self, db: Session, title: str = "New Chat") -> Conversation:
        db_conversation = Conversation(title=title)
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Conversation).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

    def get_by_id(self, db: Session, conversation_id: int):
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def update_title(self, db: Session, conversation_id: int, title: str):
        db_conv = self.get_by_id(db, conversation_id)
        if db_conv:
            db_conv.title = title
            db.commit()
            db.refresh(db_conv)
        return db_conv

    def delete(self, db: Session, conversation_id: int):
        db_conv = self.get_by_id(db, conversation_id)
        if db_conv:
            db.delete(db_conv)
            db.commit()
            return True
        return False
