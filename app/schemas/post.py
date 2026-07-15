from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PostCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=2000)
    password: str = Field(min_length=1, max_length=100)


class PostUpdateRequest(PostCreateRequest):
    pass


class PostDeleteRequest(BaseModel):
    password: str = Field(min_length=1, max_length=100)


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    view_count: int
    like_count: int
    created_at: datetime
    updated_at: datetime


class PostListResponse(BaseModel):
    items: list[PostResponse]
    page: int
    size: int
    total: int
    total_pages: int


class PostCreateResponse(BaseModel):
    id: int
