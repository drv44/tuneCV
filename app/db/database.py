from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

if settings.DATABASE_URL:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # This case should ideally not happen if DATABASE_URL is mandatory
    # Or handle it by raising an error or using a fallback like SQLite for local dev if desired
    print("CRITICAL: DATABASE_URL is not configured. Database functionality will be unavailable.")
    engine = None
    SessionLocal = None 

# Dependency to get DB session
def get_db():
    if SessionLocal is None:
        raise Exception("Database not configured. SessionLocal is None.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# # Optional: Function to create tables (useful for initial setup or tests)
# from app.db.base_class import Base
# def init_db():
#     if engine is None:
#        print("Cannot initialize database, engine is not configured.")
#        return
#     Base.metadata.create_all(bind=engine) 