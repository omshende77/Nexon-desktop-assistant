from sqlalchemy.orm import Session
from ..models import Task


class TaskRepository:
    def get_all(self, db: Session):
        return db.query(Task).order_by(Task.created_at.desc()).all()

    def get_pending(self, db: Session):
        return db.query(Task).filter(Task.completed == False).order_by(Task.created_at.desc()).all()

    def get_completed(self, db: Session):
        return db.query(Task).filter(Task.completed == True).order_by(Task.updated_at.desc()).all()

    def get_by_id(self, db: Session, task_id: int):
        return db.query(Task).filter(Task.id == task_id).first()

    def create(self, db: Session, title: str, description: str = None, priority: str = "medium", due_date: str = None):
        task = Task(title=title, description=description, priority=priority, due_date=due_date)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    def update(self, db: Session, task_id: int, **kwargs):
        task = self.get_by_id(db, task_id)
        if not task:
            return None
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        db.commit()
        db.refresh(task)
        return task

    def complete(self, db: Session, task_id: int):
        return self.update(db, task_id, completed=True)

    def delete(self, db: Session, task_id: int):
        task = self.get_by_id(db, task_id)
        if task:
            db.delete(task)
            db.commit()
        return task
