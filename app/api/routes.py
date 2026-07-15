from collections.abc import Generator

from fastapi import APIRouter, Depends

from app.core.response import CommonResponse, build_response
from app.schemas.route import PedestrianRouteRequest, PedestrianRouteResponse
from app.services.route_service import RouteService

router = APIRouter(prefix="/routes", tags=["routes"])


def get_route_service() -> Generator[RouteService, None, None]:
    service = RouteService()
    try:
        yield service
    finally:
        service.close()


@router.post("/pedestrian", response_model=CommonResponse[PedestrianRouteResponse])
def get_pedestrian_route(
    request: PedestrianRouteRequest,
    service: RouteService = Depends(get_route_service),
) -> dict[str, object]:
    payload = service.get_pedestrian_route(request)
    return build_response(200, "도보 경로 조회에 성공했습니다.", payload.model_dump())
