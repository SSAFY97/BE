import unittest

from fastapi.testclient import TestClient

from app.main import app


class AppApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_check(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["response"], 200)
        self.assertEqual(response.json()["data"]["status"], "ok")

    def test_create_and_get_post(self) -> None:
        create_response = self.client.post(
            "/api/posts",
            json={"title": "테스트 제목", "content": "테스트 내용", "password": "1234"},
        )
        self.assertEqual(create_response.status_code, 201)
        payload = create_response.json()
        self.assertEqual(payload["response"], 201)
        post_id = payload["data"]["id"]

        get_response = self.client.get(f"/api/posts/{post_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["data"]["id"], post_id)


if __name__ == "__main__":
    unittest.main()
