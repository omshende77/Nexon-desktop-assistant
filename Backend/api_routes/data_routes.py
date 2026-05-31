from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, List, Optional
from pydantic import BaseModel

from ..database.config import get_db
from ..auth_routes import get_current_user
from ..database.models import User, Task, Note, Memory, Reminder

router = APIRouter(prefix="/api/data", tags=["data"])

# --- Pydantic Models ---

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = "medium"
    due_date: Optional[str] = None

class TaskResponse(TaskCreate):
    id: int
    class Config:
        orm_mode = True

class NoteCreate(BaseModel):
    title: str
    content: str
    tags: Optional[str] = None

class NoteResponse(NoteCreate):
    id: int
    class Config:
        orm_mode = True

class MemoryCreate(BaseModel):
    key: str
    value: str
    category: str = "general"

class MemoryResponse(MemoryCreate):
    id: int
    class Config:
        orm_mode = True

class ReminderCreate(BaseModel):
    text: str
    remind_at: Optional[str] = None
    completed: bool = False

class ReminderResponse(ReminderCreate):
    id: int
    class Config:
        orm_mode = True


# --- Tasks ---

@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).filter(Task.user_id == current_user.id).all()

@router.post("/tasks", response_model=TaskResponse)
def create_task(req: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = Task(**req.dict(), user_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, req: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in req.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_item)
    db.commit()
    return {"status": "deleted"}


# --- Notes ---

@router.get("/notes", response_model=List[NoteResponse])
def get_notes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Note).filter(Note.user_id == current_user.id).all()

@router.post("/notes", response_model=NoteResponse)
def create_note(req: NoteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = Note(**req.dict(), user_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(note_id: int, req: NoteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Note not found")
    for key, value in req.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(db_item)
    db.commit()
    return {"status": "deleted"}


# --- Memories ---

@router.get("/memories", response_model=List[MemoryResponse])
def get_memories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Memory).filter(Memory.user_id == current_user.id).all()

@router.post("/memories", response_model=MemoryResponse)
def create_memory(req: MemoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = Memory(**req.dict(), user_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/memories/{memory_id}", response_model=MemoryResponse)
def update_memory(memory_id: int, req: MemoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = db.query(Memory).filter(Memory.id == memory_id, Memory.user_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Memory not found")
    for key, value in req.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/memories/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = db.query(Memory).filter(Memory.id == memory_id, Memory.user_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Memory not found")
    db.delete(db_item)
    db.commit()
    return {"status": "deleted"}


# --- Reminders ---

@router.get("/reminders", response_model=List[ReminderResponse])
def get_reminders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Reminder).filter(Reminder.user_id == current_user.id).all()

@router.post("/reminders", response_model=ReminderResponse)
def create_reminder(req: ReminderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = Reminder(**req.dict(), user_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/reminders/{reminder_id}", response_model=ReminderResponse)
def update_reminder(reminder_id: int, req: ReminderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Reminder not found")
    for key, value in req.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/reminders/{reminder_id}")
def delete_reminder(reminder_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_item = db.query(Reminder).filter(Reminder.id == reminder_id, Reminder.user_id == current_user.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(db_item)
    db.commit()
    return {"status": "deleted"}
