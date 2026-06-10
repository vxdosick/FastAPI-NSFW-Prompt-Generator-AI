from sqlalchemy import Boolean, Column, Integer, JSON, String

from db.database import Base


class User(Base):
    __tablename__ = "users"

    telegram_id = Column(String, primary_key=True, index=True)
    credits = Column(Integer, nullable=False, default=5)
    prompts = Column(JSON, nullable=True)
    is_blocked = Column(Boolean, nullable=False, default=False, server_default="false")