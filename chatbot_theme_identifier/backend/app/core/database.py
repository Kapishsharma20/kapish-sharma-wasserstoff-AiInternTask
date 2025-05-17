from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from databases import Database
from app.config import settings

DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}/{settings.DB_NAME}"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
database = Database(DATABASE_URL)
