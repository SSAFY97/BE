import unittest

from fastapi.testclient import TestClient

from app.api.routes import get_route_service
from app.main import app
from app.schemas.route import (
    PedestrianRouteResponse,
    RouteCoordinate,
)


class FakeRouteService:
    def get_pedestrian_route(self, request) -> PedestrianRouteResponse:
        return PedestrianRouteResponse(
            origin=request.origin,
            destination=request.destination,
            straight_line_distance_meters=1458,
            distance_meters=1800,
            duration_seconds=1200,
            path=[
                RouteCoordinate(latitude=37.5665, longitude=126.9780),
                RouteCoordinate(latitude=37.5796, longitude=126.9770),
            ],
        )


class RoutesApiTests(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides[get_route_service] = lambda: FakeRouteService()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.pop(get_route_service, None)

    def test_pedestrian_route_uses_common_response(self) -> None:
        response = self.client.post(
            "/api/routes/pedestrian",
            json={
                "origin": {"name": "서울시청", "latitude": 37.5665, "longitude": 126.9780},
                "destination": {"name": "경복궁", "latitude": 37.5796, "longitude": 126.9770},
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {"response", "message", "data"})
        self.assertEqual(
            set(response.json()["data"]),
            {
                "origin",
                "destination",
                "straight_line_distance_meters",
                "distance_meters",
                "duration_seconds",
                "path",
            },
        )
        self.assertEqual(response.json()["data"]["distance_meters"], 1800)
        self.assertEqual(response.json()["data"]["duration_seconds"], 1200)

    def test_invalid_coordinate_uses_common_validation_response(self) -> None:
        response = self.client.post(
            "/api/routes/pedestrian",
            json={
                "origin": {"latitude": 91, "longitude": 126.9780},
                "destination": {"latitude": 37.5796, "longitude": 126.9770},
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["response"], 422)
        self.assertIsNone(response.json()["data"])


if __name__ == "__main__":
    unittest.main()
