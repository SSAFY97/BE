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
        self.assertLessEqual(len(payload["data"]["items"]), 3)

    def test_get_location_detail(self) -> None:
        response = self.client.get("/api/locations/1059877")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["response"], 200)
        self.assertEqual(payload["data"]["id"], "1059877")


if __name__ == "__main__":
    unittest.main()
