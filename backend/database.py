from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Usamos una base de datos SQLite ubicada en la raíz del proyecto, resolviendo ruta absoluta
_base_dir = Path(__file__).resolve().parent
_db_path = (_base_dir.parent / "library.db").resolve()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{_db_path.as_posix()}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
