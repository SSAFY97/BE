from fastapi import HTTPException

from app.models.post import Post
from app.repositories.post_repository import PostRepository
from app.schemas.post import (
    PostCreateRequest,
    PostDeleteRequest,
    PostLikeResponse,
    PostListItem,
    PostListResponse,
    PostResponse,
    PostUpdateRequest,
)


class PostService:
    def __init__(self, repository: PostRepository) -> None:
        self.repository = repository

    def create_post(self, request: PostCreateRequest) -> PostResponse:
        post = self.repository.create(request.title, request.content, request.writer, request.password)
        return self._to_response(post)

    def get_post(self, post_id: int) -> PostResponse:
        post = self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

        updated_post = self.repository.increment_view_count(post_id)
        if not updated_post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        return self._to_response(updated_post)

    def list_posts(self, page: int, size: int, keyword: str | None) -> PostListResponse:
        posts, total = self.repository.list(page=page, size=size, keyword=keyword)
        total_pages = (total + size - 1) // size if total else 0
        items = [
            PostListItem(
                id=post.id,
                title=post.title,
                writer=post.writer,
                view_count=post.view_count,
                like_count=post.like_count,
                created_at=post.created_at,
            )
            for post in posts
        ]
        return PostListResponse(items=items, page=page, size=size, total=total, total_pages=total_pages)

    def update_post(self, post_id: int, request: PostUpdateRequest) -> PostResponse:
        post = self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        if post.password != request.password:
            raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

        updated_post = self.repository.update(post, request.title, request.content, request.writer)
        return self._to_response(updated_post)

    def delete_post(self, post_id: int, request: PostDeleteRequest) -> None:
        post = self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        if post.password != request.password:
            raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        self.repository.delete(post)

    def like_post(self, post_id: int) -> PostLikeResponse:
        post = self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

        updated_post = self.repository.increment_like_count(post_id)
        if not updated_post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        return PostLikeResponse(post_id=updated_post.id, like_count=updated_post.like_count)

    @staticmethod
    def _to_response(post: Post) -> PostResponse:
        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            writer=post.writer,
            view_count=post.view_count,
            like_count=post.like_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
