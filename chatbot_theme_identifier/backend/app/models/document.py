from sqlalchemy import Column, String, Text, Float, DateTime
from datetime import datetime
from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String(255), unique=True)
    file_type = Column(String(50))
    text_content = Column(Text)
    ocr_confidence = Column(Float)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    file_hash = Column(String(64), unique=True)
