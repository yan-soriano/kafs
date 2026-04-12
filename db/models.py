from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, DateTime
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    tiktok_access_token = Column(String, nullable=True)
    tiktok_refresh_token = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    file_id = Column(String, nullable=False)
    caption = Column(String, nullable=True)
    status = Column(String, default='pending') # pending, uploaded, failed
    scheduled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
