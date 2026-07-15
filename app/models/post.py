from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    writer = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    like_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
