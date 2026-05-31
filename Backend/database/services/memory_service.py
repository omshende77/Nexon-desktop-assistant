from sqlalchemy.orm import Session
from ..repositories.memory_repo import MemoryRepository


class MemoryService:
    def __init__(self):
        self.repo = MemoryRepository()

    def remember(self, db: Session, key: str, value: str, category: str = "general"):
        """Store or update a memory entry."""
        return self.repo.upsert(db, key, value, category)

    def forget(self, db: Session, key: str):
        """Remove a memory entry by key."""
        return self.repo.delete_by_key(db, key)

    def get_all(self, db: Session):
        return self.repo.get_all(db)

    def get_context_prompt(self, db: Session) -> str:
        """
        Build a prompt snippet with all stored memories to inject
        into the AI system prompt so the assistant knows about the user.
        """
        memories = self.repo.get_all(db)
        if not memories:
            return ""
        lines = ["User memory / long-term context:"]
        for m in memories:
            lines.append(f"  - {m.key}: {m.value}")
        return "\n".join(lines)
