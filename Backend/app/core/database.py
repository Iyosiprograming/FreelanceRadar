from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# 1. Create the engine
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=(settings.MODE == "development")
)

# 2. Create the Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Modern 2.0 Declarative Base
class Base(DeclarativeBase):
    pass

# 4. Database session generator (FastAPI Dependency compatible)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
