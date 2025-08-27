from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

engine = create_engine("sqlite:///bot_database.db")
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class UserAccess(Base):
    __tablename__ = "user_access"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    full_name = Column(String)
    is_paid_client = Column(Boolean, default=False)
    subscription_date = Column(DateTime, nullable=True)
    subscription_expiration = Column(DateTime, nullable=True)
    
Base.metadata.create_all(bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

