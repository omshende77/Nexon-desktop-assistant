from sqlalchemy.orm import Session
from ..repositories.message_repo import MessageRepository
from ..repositories.conversation_repo import ConversationRepository
from .conversation_service import ConversationService

class MessageService:
    def __init__(self):
        self.repo = MessageRepository()
        self.conv_service = ConversationService()

    def add_message(self, db: Session, conversation_id: int, role: str, content: str, message_type: str = "text"):
        # Auto-generate title if this is the first user message
        if role == 'user':
            messages = self.repo.get_by_conversation(db, conversation_id)
            if not messages:
                # Truncate at 40 chars and remove newlines
                title_content = content.replace("\n", " ")[:40]
                if len(content) > 40:
                    title_content += "..."
                self.conv_service.update_title(db, conversation_id, title_content)

        return self.repo.create(db, conversation_id, role, content, message_type)

    def get_conversation_history(self, db: Session, conversation_id: int):
        return self.repo.get_by_conversation(db, conversation_id)
