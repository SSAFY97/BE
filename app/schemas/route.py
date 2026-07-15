from pydantic import BaseModel, Field


class RoutePoint(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class PedestrianRouteRequest(BaseModel):
    origin: RoutePoint
    destination: RoutePoint


class RouteCoordinate(BaseModel):
    latitude: float
    longitude: float


class PedestrianRouteResponse(BaseModel):
    origin: RoutePoint
    destination: RoutePoint
    straight_line_distance_meters: int
    distance_meters: int
    duration_seconds: int
    path: list[RouteCoordinate]
