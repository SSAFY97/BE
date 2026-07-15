from sqlalchemy.orm import Session

from app.models.post import Post


class PostRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, title: str, content: str, password: str) -> Post:
        post = Post(title=title, content=content, password=password)
        self.session.add(post)
        self.session.commit()
        self.session.refresh(post)
        return post

    def get_by_id(self, post_id: int) -> Post | None:
        return self.session.query(Post).filter(Post.id == post_id).first()

    def list(self, page: int, size: int, keyword: str | None) -> tuple[list[Post], int]:
        query = self.session.query(Post)
        if keyword:
            like_pattern = f"%{keyword}%"
            query = query.filter((Post.title.like(like_pattern)) | (Post.content.like(like_pattern)))

        total = query.count()
        posts = query.order_by(Post.created_at.desc()).offset((page - 1) * size).limit(size).all()
        return posts, total

    def update(self, post: Post, title: str, content: str) -> Post:
        post.title = title
        post.content = content
        self.session.commit()
        self.session.refresh(post)
        return post

    def delete(self, post: Post) -> None:
        self.session.delete(post)
        self.session.commit()

    def increment_view_count(self, post_id: int) -> None:
        self.session.query(Post).filter(Post.id == post_id).update({Post.view_count: Post.view_count + 1})
        self.session.commit()

    def increment_like_count(self, post_id: int) -> None:
        self.session.query(Post).filter(Post.id == post_id).update({Post.like_count: Post.like_count + 1})
        self.session.commit()
