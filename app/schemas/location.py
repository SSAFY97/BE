from pydantic import BaseModel, Field


class LocationItem(BaseModel):
    id: str
    title: str
    category: str
    address: str | None = None
    tel: str | None = None
    image_url: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    content_type_id: str | None = None


class LocationListResponse(BaseModel):
    items: list[LocationItem]
    total: int


class LocationDetailResponse(LocationItem):
    pass
