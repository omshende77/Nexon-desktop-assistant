from sqlalchemy.orm import Session
from ..models import Reminder


class ReminderRepository:
    def get_all(self, db: Session):
        return db.query(Reminder).order_by(Reminder.created_at.desc()).all()

    def get_pending(self, db: Session):
        return db.query(Reminder).filter(Reminder.completed == False).order_by(Reminder.created_at.desc()).all()

    def get_by_id(self, db: Session, reminder_id: int):
        return db.query(Reminder).filter(Reminder.id == reminder_id).first()

    def create(self, db: Session, text: str, remind_at: str = None):
        reminder = Reminder(text=text, remind_at=remind_at)
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    def complete(self, db: Session, reminder_id: int):
        r = self.get_by_id(db, reminder_id)
        if r:
            r.completed = True
            db.commit()
            db.refresh(r)
        return r

    def delete(self, db: Session, reminder_id: int):
        r = self.get_by_id(db, reminder_id)
        if r:
            db.delete(r)
            db.commit()
        return r
