# app_db.py
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Use pg8000 driver by default (avoids Termux build issues)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+pg8000://user:password@localhost:5432/outbound_ai")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class CallLog(Base):
    __tablename__ = "call_logs"
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String, unique=True)
    phone_number = Column(String)
    campaign_id = Column(String)
    duration = Column(Integer)
    status = Column(String)
    timestamp = Column(DateTime)

def init_db():
    Base.metadata.create_all(bind=engine)
