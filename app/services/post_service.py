from fastapi import HTTPException

from app.repositories.post_repository import PostRepository
from app.schemas.post import PostCreateRequest, PostDeleteRequest, PostResponse, PostListResponse, PostCreateResponse, PostUpdateRequest


class PostService:
    def __init__(self, repository: PostRepository) -> None:
        self.repository = repository

    def create_post(self, request: PostCreateRequest) -> PostCreateResponse:
        post = self.repository.create(request.title, request.content, request.password)
        return PostCreateResponse(id=post.id)

    def get_post(self, post_id: int) -> PostResponse:
        post = self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

        self.repository.increment_view_count(post_id)
        post.view_count += 1
        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            view_count=post.view_count,
            like_count=post.like_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )

    def list_posts(self, page: int, size: int, keyword: str | None) -> PostListResponse:
        posts, total = self.repository.list(page=page, size=size, keyword=keyword)
        total_pages = (total + size - 1) // size if total else 0
        items = [
            PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                view_count=post.view_count,
                like_count=post.like_count,
                created_at=post.created_at,
                updated_at=post.updated_at,
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

        updated_post = self.repository.update(post, request.title, request.content)
        return PostResponse(
            id=updated_post.id,
            title=updated_post.title,
            content=updated_post.content,
            view_count=updated_post.view_count,
            like_count=updated_post.like_count,
            created_at=updated_post.created_at,
            updated_at=updated_post.updated_at,
        )

    def delete_post(self, post_id: int, request: PostDeleteRequest) -> None:
        post = self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
        if post.password != request.password:
            raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        self.repository.delete(post)

    def like_post(self, post_id: int) -> PostResponse:
        post = self.repository.get_by_id(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

        self.repository.increment_like_count(post_id)
        post.like_count += 1
        return PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            view_count=post.view_count,
            like_count=post.like_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
        )
