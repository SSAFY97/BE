import unittest

from fastapi import HTTPException

from app.schemas.route import PedestrianRouteRequest, RoutePoint
from app.services.route_service import RouteService


class FakeTmapClient:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.call_count = 0

    def get_pedestrian_route(self, **_: object) -> dict:
        self.call_count += 1
        return self.payload

    def close(self) -> None:
        pass


def build_request(
    *,
    origin_latitude: float = 37.5665,
    origin_longitude: float = 126.9780,
    destination_latitude: float = 37.5796,
    destination_longitude: float = 126.9770,
) -> PedestrianRouteRequest:
    return PedestrianRouteRequest(
        origin=RoutePoint(
            name="출발지",
            latitude=origin_latitude,
            longitude=origin_longitude,
        ),
        destination=RoutePoint(
            name="도착지",
            latitude=destination_latitude,
            longitude=destination_longitude,
        ),
    )


def route_payload(distance: int = 1800) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [126.9780, 37.5665]},
                "properties": {
                    "totalDistance": distance,
                    "totalTime": 1200,
                    "pointIndex": 0,
                    "description": "세종대로를 따라 이동",
                    "turnType": 200,
                    "pointType": "S",
                },
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [126.9780, 37.5665],
                        [126.9775, 37.5730],
                        [126.9770, 37.5796],
                    ],
                },
                "properties": {"distance": distance, "time": 1200},
            },
        ],
    }


class RouteServiceTests(unittest.TestCase):
    def test_normalizes_tmap_pedestrian_route(self) -> None:
        client = FakeTmapClient(route_payload())
        response = RouteService(client=client).get_pedestrian_route(build_request())

        self.assertEqual(response.distance_meters, 1800)
        self.assertEqual(response.duration_seconds, 1200)
        self.assertEqual(len(response.path), 3)
        self.assertEqual(response.path[0].latitude, 37.5665)
        self.assertEqual(response.path[0].longitude, 126.9780)

    def test_rejects_points_over_ten_kilometers_before_external_call(self) -> None:
        client = FakeTmapClient(route_payload())
        service = RouteService(client=client)

        with self.assertRaises(HTTPException) as context:
            service.get_pedestrian_route(
                build_request(destination_latitude=37.70, destination_longitude=126.9780)
            )

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(client.call_count, 0)

    def test_rejects_returned_route_over_ten_kilometers(self) -> None:
        client = FakeTmapClient(route_payload(distance=10_001))

        with self.assertRaises(HTTPException) as context:
            RouteService(client=client).get_pedestrian_route(build_request())

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(client.call_count, 1)

    def test_rejects_same_origin_and_destination(self) -> None:
        client = FakeTmapClient(route_payload())

        with self.assertRaises(HTTPException) as context:
            RouteService(client=client).get_pedestrian_route(
                build_request(
                    destination_latitude=37.5665,
                    destination_longitude=126.9780,
                )
            )

        self.assertEqual(context.exception.status_code, 422)
        self.assertEqual(client.call_count, 0)


if __name__ == "__main__":
    unittest.main()
