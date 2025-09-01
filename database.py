from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime,BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DB_DSN = "postgresql://botuser:5JaZI1REfMd3y1WUrpDXLEeGfFi1ddNI@dpg-d2r15undiees73dnvnb0-a/botdb_oefx"
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
    
Base.metadata.create_all(bind=engine)

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

