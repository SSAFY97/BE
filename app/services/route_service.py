from math import asin, cos, radians, sin, sqrt
from typing import Any

from fastapi import HTTPException

from app.clients.tmap_client import TmapClient, TmapClientError, TmapClientTimeoutError
from app.schemas.route import (
    PedestrianRouteRequest,
    PedestrianRouteResponse,
    RouteCoordinate,
)

MAX_ROUTE_DISTANCE_METERS = 10_000
EARTH_RADIUS_METERS = 6_371_000


class RouteService:
    def __init__(self, client: TmapClient | None = None) -> None:
        self.client = client or TmapClient()

    def get_pedestrian_route(self, request: PedestrianRouteRequest) -> PedestrianRouteResponse:
        straight_line_distance = self._calculate_distance_meters(
            request.origin.latitude,
            request.origin.longitude,
            request.destination.latitude,
            request.destination.longitude,
        )
        if straight_line_distance < 1:
            raise HTTPException(status_code=422, detail="출발지와 도착지는 서로 달라야 합니다.")
        if straight_line_distance > MAX_ROUTE_DISTANCE_METERS:
            raise HTTPException(status_code=422, detail="출발지와 도착지는 10km 이내여야 합니다.")

        try:
            payload = self.client.get_pedestrian_route(
                start_latitude=request.origin.latitude,
                start_longitude=request.origin.longitude,
                end_latitude=request.destination.latitude,
                end_longitude=request.destination.longitude,
                start_name=request.origin.name or "출발지",
                end_name=request.destination.name or "도착지",
            )
        except TmapClientTimeoutError as exc:
            raise HTTPException(status_code=504, detail="경로 안내 서비스 응답이 지연되고 있습니다.") from exc
        except TmapClientError as exc:
            if exc.status_code in (401, 403):
                raise HTTPException(status_code=500, detail="경로 안내 서비스 설정에 오류가 있습니다.") from exc
            raise HTTPException(status_code=503, detail="경로 안내 서비스를 일시적으로 이용할 수 없습니다.") from exc

        return self._to_response(request, straight_line_distance, payload)

    def close(self) -> None:
        self.client.close()

    @staticmethod
    def _calculate_distance_meters(
        start_latitude: float,
        start_longitude: float,
        end_latitude: float,
        end_longitude: float,
    ) -> float:
        latitude_delta = radians(end_latitude - start_latitude)
        longitude_delta = radians(end_longitude - start_longitude)
        start_latitude_radians = radians(start_latitude)
        end_latitude_radians = radians(end_latitude)
        haversine = (
            sin(latitude_delta / 2) ** 2
            + cos(start_latitude_radians)
            * cos(end_latitude_radians)
            * sin(longitude_delta / 2) ** 2
        )
        return 2 * EARTH_RADIUS_METERS * asin(sqrt(haversine))

    def _to_response(
        self,
        request: PedestrianRouteRequest,
        straight_line_distance: float,
        payload: dict[str, Any],
    ) -> PedestrianRouteResponse:
        features = payload.get("features")
        if not isinstance(features, list) or not features:
            raise HTTPException(status_code=404, detail="이동 가능한 도보 경로를 찾을 수 없습니다.")

        summary_properties = self._find_summary_properties(features)
        route_distance = self._as_non_negative_int(summary_properties.get("totalDistance"))
        route_duration = self._as_non_negative_int(summary_properties.get("totalTime"))
        if route_distance is None or route_duration is None:
            raise HTTPException(status_code=503, detail="경로 안내 서비스를 일시적으로 이용할 수 없습니다.")
        if route_distance > MAX_ROUTE_DISTANCE_METERS:
            raise HTTPException(status_code=422, detail="조회된 도보 경로가 10km를 초과합니다.")

        path = self._extract_path(features)
        if not path:
            raise HTTPException(status_code=404, detail="이동 가능한 도보 경로를 찾을 수 없습니다.")

        return PedestrianRouteResponse(
            origin=request.origin,
            destination=request.destination,
            straight_line_distance_meters=round(straight_line_distance),
            distance_meters=route_distance,
            duration_seconds=route_duration,
            path=path,
        )

    @staticmethod
    def _find_summary_properties(features: list[Any]) -> dict[str, Any]:
        for feature in features:
            if not isinstance(feature, dict):
                continue
            properties = feature.get("properties")
            if isinstance(properties, dict) and "totalDistance" in properties:
                return properties
        return {}

    @staticmethod
    def _extract_path(features: list[Any]) -> list[RouteCoordinate]:
        path: list[RouteCoordinate] = []
        for feature in features:
            if not isinstance(feature, dict):
                continue
            geometry = feature.get("geometry")
            if not isinstance(geometry, dict) or geometry.get("type") != "LineString":
                continue
            coordinates = geometry.get("coordinates")
            if not isinstance(coordinates, list):
                continue
            for coordinate in coordinates:
                if not isinstance(coordinate, list) or len(coordinate) < 2:
                    continue
                try:
                    point = RouteCoordinate(latitude=float(coordinate[1]), longitude=float(coordinate[0]))
                except (TypeError, ValueError):
                    continue
                if not path or point != path[-1]:
                    path.append(point)
        return path

    @staticmethod
    def _as_non_negative_int(value: Any) -> int | None:
        try:
            converted = int(value)
        except (TypeError, ValueError):
            return None
        return converted if converted >= 0 else None
