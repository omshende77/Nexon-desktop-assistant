from sqlalchemy.orm import Session
from ..models import Conversation

class ConversationRepository:
    def create(self, db: Session, title: str = "New Chat", user_id: int = None) -> Conversation:
        db_conversation = Conversation(title=title, user_id=user_id)
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        return db_conversation

    def get_all(self, db: Session, user_id: int = None, skip: int = 0, limit: int = 100):
        query = db.query(Conversation)
        if user_id is not None:
            query = query.filter(Conversation.user_id == user_id)
        return query.order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

    def get_by_id(self, db: Session, conversation_id: int, user_id: int = None):
        query = db.query(Conversation).filter(Conversation.id == conversation_id)
        if user_id is not None:
            query = query.filter(Conversation.user_id == user_id)
        return query.first()

    def update_title(self, db: Session, conversation_id: int, title: str, user_id: int = None):
        db_conv = self.get_by_id(db, conversation_id, user_id)
        if db_conv:
            db_conv.title = title
            db.commit()
            db.refresh(db_conv)
        return db_conv

    def delete(self, db: Session, conversation_id: int, user_id: int = None):
        db_conv = self.get_by_id(db, conversation_id, user_id)
        if db_conv:
            db.delete(db_conv)
            db.commit()
            return True
        return False
