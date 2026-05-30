from .config import Base, engine, DB_AVAILABLE
import sqlalchemy

def init_database():
    if not DB_AVAILABLE:
        print("[Database] Init skipped: DB not available.")
        return False
        
    try:
        # Base.metadata.create_all(bind=engine)
        print("[Database] Initialization complete. (Using Alembic for migrations).")
        return True
    except Exception as e:
        print(f"[Database] Error initializing database: {e}")
        return False
