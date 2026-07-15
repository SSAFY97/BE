from typing import Generator

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.response import CommonResponse, build_response
from app.repositories.post_repository import PostRepository
from app.schemas.post import (
    PostCreateRequest,
    PostDeleteRequest,
    PostLikeResponse,
    PostListResponse,
    PostResponse,
    PostUpdateRequest,
)
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    repository = PostRepository(db)
    return PostService(repository=repository)


@router.get("", response_model=CommonResponse[PostListResponse])
def list_posts(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    keyword: str | None = None,
    service: PostService = Depends(get_post_service),
) -> dict[str, object]:
    payload = service.list_posts(page=page, size=size, keyword=keyword)
    return build_response(200, "게시글 목록 조회에 성공했습니다.", payload.model_dump())


@router.get("/{post_id}", response_model=CommonResponse[PostResponse])
def get_post(post_id: int, service: PostService = Depends(get_post_service)) -> dict[str, object]:
    payload = service.get_post(post_id)
    return build_response(200, "게시글 조회에 성공했습니다.", payload.model_dump())


@router.post("", response_model=CommonResponse[PostResponse], status_code=201)
def create_post(request: PostCreateRequest, service: PostService = Depends(get_post_service)) -> dict[str, object]:
    payload = service.create_post(request)
    return build_response(201, "게시글 작성에 성공했습니다.", payload.model_dump())


@router.put("/{post_id}", response_model=CommonResponse[PostResponse])
def update_post(
    post_id: int,
    request: PostUpdateRequest,
    service: PostService = Depends(get_post_service),
) -> dict[str, object]:
    payload = service.update_post(post_id, request)
    return build_response(200, "게시글 수정에 성공했습니다.", payload.model_dump())


@router.delete("/{post_id}", response_model=CommonResponse[None])
def delete_post(
    post_id: int,
    request: PostDeleteRequest,
    service: PostService = Depends(get_post_service),
) -> dict[str, object]:
    service.delete_post(post_id, request)
    return build_response(200, "게시글 삭제에 성공했습니다.", None)


@router.post("/{post_id}/likes", response_model=CommonResponse[PostLikeResponse])
def like_post(post_id: int, service: PostService = Depends(get_post_service)) -> dict[str, object]:
    payload = service.like_post(post_id)
    return build_response(200, "게시글 좋아요에 성공했습니다.", payload.model_dump())
