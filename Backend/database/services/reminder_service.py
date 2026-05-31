from sqlalchemy.orm import Session
from ..repositories.reminder_repo import ReminderRepository


class ReminderService:
    def __init__(self):
        self.repo = ReminderRepository()

    def create_reminder(self, db: Session, text: str, remind_at: str = None):
        return self.repo.create(db, text.strip(), remind_at)

    def get_all_reminders(self, db: Session):
        return self.repo.get_all(db)

    def get_pending_reminders(self, db: Session):
        return self.repo.get_pending(db)

    def complete_reminder(self, db: Session, reminder_id: int):
        return self.repo.complete(db, reminder_id)

    def delete_reminder(self, db: Session, reminder_id: int):
        return self.repo.delete(db, reminder_id)
