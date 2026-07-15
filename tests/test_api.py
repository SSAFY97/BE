import unittest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.posts import get_db
from app.core.database import Base
from app.main import app
from app.models.post import Post


class AppApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.session_factory = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)

        def override_get_db():
            db = cls.session_factory()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls) -> None:
        app.dependency_overrides.clear()
        cls.engine.dispose()

    def setUp(self) -> None:
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def create_post(
        self,
        *,
        title: str = "테스트 제목",
        content: str = "테스트 내용",
        writer: str = "익명 사용자",
        password: str = "1234",
    ):
        return self.client.post(
            "/api/posts",
            json={"title": title, "content": content, "writer": writer, "password": password},
        )

    def test_health_check(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["response"], 200)
        self.assertEqual(response.json()["data"]["status"], "ok")

    def test_create_and_get_post_preserves_writer_without_password(self) -> None:
        create_response = self.create_post()

        self.assertEqual(create_response.status_code, 201)
        created = create_response.json()["data"]
        self.assertEqual(created["writer"], "익명 사용자")
        self.assertNotIn("password", created)

        get_response = self.client.get(f"/api/posts/{created['id']}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["data"]["view_count"], 1)

        with self.session_factory() as session:
            stored = session.get(Post, created["id"])
            self.assertEqual(stored.view_count, 1)
            self.assertEqual(stored.writer, "익명 사용자")

    def test_list_search_returns_summary_and_pagination(self) -> None:
        self.create_post(title="서울 축제 후기", content="즐거웠습니다")
        self.create_post(title="다른 글", content="서울 축제를 추천합니다")

        response = self.client.get("/api/posts?keyword=축제&page=1&size=1")
        data = response.json()["data"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["total"], 2)
        self.assertEqual(data["total_pages"], 2)
        self.assertEqual(len(data["items"]), 1)
        self.assertNotIn("content", data["items"][0])
        self.assertNotIn("password", data["items"][0])

    def test_update_and_delete_require_matching_password(self) -> None:
        post_id = self.create_post().json()["data"]["id"]
        update_body = {
            "title": "수정 제목",
            "content": "수정 내용",
            "writer": "수정 작성자",
            "password": "9999",
        }

        forbidden = self.client.put(f"/api/posts/{post_id}", json=update_body)
        self.assertEqual(forbidden.status_code, 403)
        self.assertEqual(set(forbidden.json()), {"response", "message", "data"})

        forbidden_delete = self.client.request(
            "DELETE", f"/api/posts/{post_id}", json={"password": "9999"}
        )
        self.assertEqual(forbidden_delete.status_code, 403)
        self.assertEqual(forbidden_delete.json()["response"], 403)

        update_body["password"] = "1234"
        updated = self.client.put(f"/api/posts/{post_id}", json=update_body)
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["data"]["writer"], "수정 작성자")

        deleted = self.client.request(
            "DELETE", f"/api/posts/{post_id}", json={"password": "1234"}
        )
        self.assertEqual(deleted.status_code, 200)
        self.assertIsNone(deleted.json()["data"])

    def test_like_count_matches_database(self) -> None:
        post_id = self.create_post().json()["data"]["id"]

        response = self.client.post(f"/api/posts/{post_id}/likes")

        self.assertEqual(response.json()["data"], {"post_id": post_id, "like_count": 1})
        with self.session_factory() as session:
            self.assertEqual(session.get(Post, post_id).like_count, 1)

    def test_not_found_uses_common_response(self) -> None:
        response = self.client.get("/api/posts/999999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["response"], 404)
        self.assertIsNone(response.json()["data"])
        self.assertNotIn("detail", response.json())

    def test_invalid_password_and_pagination_return_422(self) -> None:
        invalid_password = self.create_post(password="123")
        invalid_page = self.client.get("/api/posts?page=0&size=0")

        self.assertEqual(invalid_password.status_code, 422)
        self.assertEqual(invalid_password.json()["response"], 422)
        self.assertEqual(invalid_page.status_code, 422)
        self.assertEqual(invalid_page.json()["response"], 422)

    def test_chat_validation_uses_common_response(self) -> None:
        response = self.client.post("/api/chat", json={})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["response"], 422)


if __name__ == "__main__":
    unittest.main()
