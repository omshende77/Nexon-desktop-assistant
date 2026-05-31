from .config import Base, engine, DB_AVAILABLE


def init_database():
    if not DB_AVAILABLE:
        print("[Database] Init skipped: DB not available.")
        return False

    try:
        # Create all tables defined in models.py that don't exist yet
        Base.metadata.create_all(bind=engine)
        print("[Database] All tables created / verified OK.")
        return True
    except Exception as e:
        print(f"[Database] Error initializing database: {e}")
        return False
