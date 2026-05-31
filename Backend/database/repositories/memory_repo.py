from sqlalchemy.orm import Session
from ..models import Memory


class MemoryRepository:
    def get_all(self, db: Session):
        return db.query(Memory).order_by(Memory.updated_at.desc()).all()

    def get_by_key(self, db: Session, key: str):
        return db.query(Memory).filter(Memory.key == key.lower()).first()

    def get_by_category(self, db: Session, category: str):
        return db.query(Memory).filter(Memory.category == category).all()

    def upsert(self, db: Session, key: str, value: str, category: str = "general"):
        """Insert or update a memory entry by key."""
        existing = self.get_by_key(db, key.lower())
        if existing:
            existing.value    = value
            existing.category = category
            db.commit()
            db.refresh(existing)
            return existing
        mem = Memory(key=key.lower(), value=value, category=category)
        db.add(mem)
        db.commit()
        db.refresh(mem)
        return mem

    def delete_by_key(self, db: Session, key: str):
        mem = self.get_by_key(db, key.lower())
        if mem:
            db.delete(mem)
            db.commit()
        return mem

    def delete_by_id(self, db: Session, memory_id: int):
        mem = db.query(Memory).filter(Memory.id == memory_id).first()
        if mem:
            db.delete(mem)
            db.commit()
        return mem
