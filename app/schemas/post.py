from datetime import datetime
from pydantic import BaseModel, Field


class PostCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=2000)
    writer: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=4, max_length=100)


class PostUpdateRequest(PostCreateRequest):
    pass


class PostDeleteRequest(BaseModel):
    password: str = Field(min_length=4, max_length=100)


class PostListItem(BaseModel):
    id: int
    title: str
    writer: str
    view_count: int
    like_count: int
    created_at: datetime


class PostResponse(PostListItem):
    content: str
    updated_at: datetime


class PostListResponse(BaseModel):
    items: list[PostListItem]
    page: int
    size: int
    total: int
    total_pages: int


class PostLikeResponse(BaseModel):
    post_id: int
    like_count: int
