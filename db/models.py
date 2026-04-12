from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Integer
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)  # telegram user id
    tiktok_access_token = Column(String, nullable=True)
    tiktok_open_id = Column(String, nullable=True)
    tiktok_username = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    file_url = Column(String, nullable=False)  # ссылка на R2/S3
    description = Column(String, nullable=True)  # AI генерированное
    hashtags = Column(String, nullable=True)
    scheduled_at = Column(DateTime, nullable=False)  # когда постить
    posted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)