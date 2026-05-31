from sqlalchemy.orm import Session
from ..repositories.note_repo import NoteRepository


class NoteService:
    def __init__(self):
        self.repo = NoteRepository()

    def save_note(self, db: Session, title: str, content: str, tags: str = None):
        return self.repo.create(db, title.strip(), content.strip(), tags)

    def get_all_notes(self, db: Session):
        return self.repo.get_all(db)

    def search_notes(self, db: Session, query: str):
        return self.repo.search(db, query)

    def update_note(self, db: Session, note_id: int, **kwargs):
        return self.repo.update(db, note_id, **kwargs)

    def delete_note(self, db: Session, note_id: int):
        return self.repo.delete(db, note_id)
