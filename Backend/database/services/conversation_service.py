from sqlalchemy.orm import Session
from ..repositories.conversation_repo import ConversationRepository

class ConversationService:
    def __init__(self):
        self.repo = ConversationRepository()

    def create_conversation(self, db: Session, title: str = "New Chat", user_id: int = None):
        return self.repo.create(db, title, user_id)

    def get_all_conversations(self, db: Session, user_id: int = None):
        return self.repo.get_all(db, user_id)

    def get_conversation(self, db: Session, conversation_id: int, user_id: int = None):
        return self.repo.get_by_id(db, conversation_id, user_id)

    def update_title(self, db: Session, conversation_id: int, title: str, user_id: int = None):
        return self.repo.update_title(db, conversation_id, title, user_id)

    def delete_conversation(self, db: Session, conversation_id: int, user_id: int = None):
        return self.repo.delete(db, conversation_id, user_id)
