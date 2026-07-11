from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/outbound_ai_calling")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Test connections before using them
    pool_recycle=3600    # Recycle connections after 1 hour
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Database models
class CallLog(Base):
    """Call log model for storing call analytics"""
    __tablename__ = "call_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    campaign_id = Column(String, index=True)
    duration = Column(Integer, default=0)
    status = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'call_id': self.call_id,
            'phone_number': self.phone_number,
            'campaign_id': self.campaign_id,
            'duration': self.duration,
            'status': self.status,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

# Dependency for FastAPI/Flask
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
