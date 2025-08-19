import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")  # development o production
DATABASE_ENGINE = os.getenv("DATABASE_ENGINE", "sqlite")  # sqlite o postgres
DATABASE_URL = os.getenv("DATABASE_URL")  # se usa solo si se define

if ENVIRONMENT == "development":
    if DATABASE_ENGINE == "sqlite":
        print("⚙️  Entorno: Desarrollo (SQLite)")
        DATABASE_URL = DATABASE_URL or "sqlite:///./dev.db"
        connect_args = {"check_same_thread": False}
    elif DATABASE_ENGINE == "postgres":
        print("⚙️  Entorno: Desarrollo (PostgreSQL local)")
        DATABASE_URL = DATABASE_URL or "postgresql://postgres:postgres@localhost:5432/dev_db"
        connect_args = {}
else:
    print("🚀 Entorno: Producción (PostgreSQL)")
    DATABASE_URL = DATABASE_URL or "postgresql://postgres:postgres@localhost:5432/prod_db"
    connect_args = {}

# Crear engine según motor
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
