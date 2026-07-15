from fastapi import APIRouter, HTTPException, Query

from app.core.response import build_response
from app.schemas.location import LocationDetailResponse, LocationListResponse
from app.services.location_service import LocationService

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("", response_model=dict)
def list_locations(
    category: str | None = None,
    keyword: str | None = None,
    limit: int | None = Query(default=None, ge=1),
) -> dict[str, object]:
    service = LocationService()
    payload = service.get_locations(category=category, keyword=keyword, limit=limit)
    return build_response(200, "지역 정보 조회에 성공했습니다.", payload.model_dump())


@router.get("/{location_id}", response_model=dict)
def get_location(location_id: str) -> dict[str, object]:
    service = LocationService()
    try:
        payload = service.get_location_by_id(location_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="지역 정보를 찾을 수 없습니다.") from exc
    return build_response(200, "지역 정보 조회에 성공했습니다.", payload.model_dump())
