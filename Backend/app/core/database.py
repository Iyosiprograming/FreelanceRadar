from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings, BASE_DIR

# 1. Anchor relative SQLite URLs to the backend directory
db_url = settings.DATABASE_URL
if db_url.startswith("sqlite:///./") or db_url == "sqlite:///test.db":
    db_file = (BASE_DIR / "test.db").resolve().as_posix()
    db_url = f"sqlite:///{db_file}"

connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    echo=False  # Set to False to keep console logs clean and hide raw SQL statements
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
