import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Cargar .env en desarrollo local (Render inyecta las vars automáticamente)
load_dotenv()

# Render inyecta DATABASE_URL cuando enlazas la BD PostgreSQL
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://contactos_user:contactos_pass@localhost:5432/contactos_db"
)

# Render usa postgres:// pero SQLAlchemy 2.x requiere postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
