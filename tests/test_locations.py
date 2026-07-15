import unittest

from fastapi.testclient import TestClient

from app.main import app


class LocationApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_list_locations(self) -> None:
        response = self.client.get("/api/locations?limit=3")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["response"], 200)
        self.assertIn("items", payload["data"])
        self.assertEqual(len(payload["data"]["items"]), 3)
        self.assertGreater(payload["data"]["total"], 3)
        self.assertNotIn("limit", payload["data"])

    def test_get_location_detail(self) -> None:
        response = self.client.get("/api/locations/1059877")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["response"], 200)
        self.assertEqual(payload["data"]["id"], "1059877")

    def test_location_not_found_uses_common_response(self) -> None:
        response = self.client.get("/api/locations/not-found")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["response"], 404)
        self.assertIsNone(response.json()["data"])
        self.assertNotIn("detail", response.json())

    def test_invalid_limit_returns_422(self) -> None:
        response = self.client.get("/api/locations?limit=0")

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["response"], 422)


if __name__ == "__main__":
    unittest.main()
