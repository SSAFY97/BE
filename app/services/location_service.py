import json
from pathlib import Path
from typing import Any

from app.schemas.location import LocationDetailResponse, LocationItem, LocationListResponse


class LocationService:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path(__file__).resolve().parents[2] / "서울"

    def _load_data(self) -> list[dict[str, Any]]:
        locations: list[dict[str, Any]] = []
        for path in sorted(self.data_dir.glob("*.json")):
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            items = payload.get("items", []) if isinstance(payload, dict) else []
            for item in items:
                location_id = str(item.get("contentid") or "")
                title = item.get("title") or ""
                address = item.get("addr1") or ""
                category = path.stem.replace("서울_", "").replace("_", " ")
                locations.append(
                    {
                        "id": location_id,
                        "title": title,
                        "category": category,
                        "address": address,
                        "tel": item.get("tel") or None,
                        "image_url": item.get("firstimage") or None,
                        "latitude": item.get("mapy") or None,
                        "longitude": item.get("mapx") or None,
                        "content_type_id": item.get("contenttypeid") or None,
                    }
                )
        return locations

    def get_locations(self, category: str | None = None, keyword: str | None = None, limit: int | None = None) -> LocationListResponse:
        locations = self._load_data()
        filtered = locations

        if category:
            filtered = [item for item in filtered if item["category"].lower() == category.lower()]

        if keyword:
            keyword_lower = keyword.lower()
            filtered = [
                item
                for item in filtered
                if keyword_lower in item["title"].lower() or keyword_lower in item.get("address", "").lower()
            ]

        if limit is not None:
            filtered = filtered[:limit]

        items = [LocationItem(**item) for item in filtered]
        return LocationListResponse(items=items, total=len(items), limit=limit or len(items))

    def get_location_by_id(self, location_id: str) -> LocationDetailResponse:
        locations = self._load_data()
        for item in locations:
            if item["id"] == location_id:
                return LocationDetailResponse(**item)
        raise KeyError(location_id)
