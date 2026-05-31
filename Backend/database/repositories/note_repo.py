from sqlalchemy.orm import Session
from ..models import Note


class NoteRepository:
    def get_all(self, db: Session):
        return db.query(Note).order_by(Note.updated_at.desc()).all()

    def search(self, db: Session, query: str):
        q = f"%{query}%"
        return db.query(Note).filter(
            (Note.title.ilike(q)) | (Note.content.ilike(q)) | (Note.tags.ilike(q))
        ).order_by(Note.updated_at.desc()).all()

    def get_by_id(self, db: Session, note_id: int):
        return db.query(Note).filter(Note.id == note_id).first()

    def create(self, db: Session, title: str, content: str, tags: str = None):
        note = Note(title=title, content=content, tags=tags)
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    def update(self, db: Session, note_id: int, **kwargs):
        note = self.get_by_id(db, note_id)
        if not note:
            return None
        for key, value in kwargs.items():
            if hasattr(note, key):
                setattr(note, key, value)
        db.commit()
        db.refresh(note)
        return note

    def delete(self, db: Session, note_id: int):
        note = self.get_by_id(db, note_id)
        if note:
            db.delete(note)
            db.commit()
        return note
