import json
import unittest

import httpx

from app.clients.tmap_client import TmapClient


class TmapClientTests(unittest.TestCase):
    def test_sends_api_key_and_wgs84_coordinates_in_tmap_order(self) -> None:
        captured: dict[str, object] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["app_key"] = request.headers.get("appKey")
            captured["body"] = json.loads(request.content)
            return httpx.Response(200, json={"type": "FeatureCollection", "features": []})

        http_client = httpx.Client(transport=httpx.MockTransport(handler))
        client = TmapClient(api_key="test-key", http_client=http_client)

        client.get_pedestrian_route(
            start_latitude=37.5665,
            start_longitude=126.9780,
            end_latitude=37.5796,
            end_longitude=126.9770,
            start_name="출발지",
            end_name="도착지",
        )

        body = captured["body"]
        self.assertEqual(captured["app_key"], "test-key")
        self.assertEqual(body["startX"], 126.9780)
        self.assertEqual(body["startY"], 37.5665)
        self.assertEqual(body["endX"], 126.9770)
        self.assertEqual(body["endY"], 37.5796)
        self.assertEqual(body["startName"], "%EC%B6%9C%EB%B0%9C%EC%A7%80")
        self.assertEqual(body["endName"], "%EB%8F%84%EC%B0%A9%EC%A7%80")
        self.assertNotIn("appKey", body)
        http_client.close()


if __name__ == "__main__":
    unittest.main()
