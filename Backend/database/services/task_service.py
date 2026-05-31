from sqlalchemy.orm import Session
from ..repositories.task_repo import TaskRepository


class TaskService:
    def __init__(self):
        self.repo = TaskRepository()

    def create_task(self, db: Session, title: str, description: str = None, priority: str = "medium", due_date: str = None):
        return self.repo.create(db, title.strip(), description, priority, due_date)

    def get_all_tasks(self, db: Session):
        return self.repo.get_all(db)

    def get_pending_tasks(self, db: Session):
        return self.repo.get_pending(db)

    def complete_task(self, db: Session, task_id: int):
        return self.repo.complete(db, task_id)

    def delete_task(self, db: Session, task_id: int):
        return self.repo.delete(db, task_id)

    def update_task(self, db: Session, task_id: int, **kwargs):
        return self.repo.update(db, task_id, **kwargs)
