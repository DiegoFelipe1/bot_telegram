import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime,BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from dotenv import load_dotenv

load_dotenv()
DB_DSN = os.getenv("DB_DSN")

engine = create_engine(DB_DSN)
SessionLocal = sessionmaker(bind=engine)


Base = declarative_base()
Base.metadata.create_all(bind=engine)

class UserAccess(Base):
    __tablename__ = "user_access"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True)
    full_name = Column(String)
    is_paid_client = Column(Boolean, default=False)
    subscription_date = Column(DateTime, nullable=True)
    subscription_expiration = Column(DateTime, nullable=True)

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    file_id = Column(String, unique=True)


Base.metadata.create_all(bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

