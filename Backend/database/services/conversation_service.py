from sqlalchemy.orm import Session
from ..repositories.conversation_repo import ConversationRepository

class ConversationService:
    def __init__(self):
        self.repo = ConversationRepository()

    def create_conversation(self, db: Session, title: str = "New Chat"):
        return self.repo.create(db, title)

    def get_all_conversations(self, db: Session):
        return self.repo.get_all(db)

    def get_conversation(self, db: Session, conversation_id: int):
        return self.repo.get_by_id(db, conversation_id)

    def update_title(self, db: Session, conversation_id: int, title: str):
        return self.repo.update_title(db, conversation_id, title)

    def delete_conversation(self, db: Session, conversation_id: int):
        return self.repo.delete(db, conversation_id)
