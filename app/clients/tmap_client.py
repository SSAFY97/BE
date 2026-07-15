from typing import Any
from urllib.parse import quote

import httpx

from app.core.config import TMAP_API_KEY, TMAP_API_TIMEOUT_SECONDS


class TmapClientError(Exception):
    def __init__(self, status_code: int | None = None) -> None:
        super().__init__("TMAP API request failed")
        self.status_code = status_code


class TmapClientTimeoutError(TmapClientError):
    pass


class TmapClient:
    PEDESTRIAN_ROUTE_URL = "https://apis.openapi.sk.com/tmap/routes/pedestrian"

    def __init__(
        self,
        api_key: str = TMAP_API_KEY,
        timeout_seconds: float = TMAP_API_TIMEOUT_SECONDS,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key.strip()
        self._owns_http_client = http_client is None
        self.http_client = http_client or httpx.Client(timeout=timeout_seconds)

    def get_pedestrian_route(
        self,
        *,
        start_latitude: float,
        start_longitude: float,
        end_latitude: float,
        end_longitude: float,
        start_name: str,
        end_name: str,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise TmapClientError(status_code=401)

        request_body = {
            "startX": start_longitude,
            "startY": start_latitude,
            "endX": end_longitude,
            "endY": end_latitude,
            "reqCoordType": "WGS84GEO",
            "resCoordType": "WGS84GEO",
            "startName": quote(start_name, safe=""),
            "endName": quote(end_name, safe=""),
            "searchOption": "0",
            "sort": "index",
        }

        try:
            response = self.http_client.post(
                self.PEDESTRIAN_ROUTE_URL,
                params={"version": "1", "format": "json"},
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "appKey": self.api_key,
                },
                json=request_body,
            )
            response.raise_for_status()
            payload = response.json()
        except httpx.TimeoutException as exc:
            raise TmapClientTimeoutError() from exc
        except httpx.HTTPStatusError as exc:
            raise TmapClientError(status_code=exc.response.status_code) from exc
        except (httpx.RequestError, ValueError) as exc:
            raise TmapClientError() from exc

        if not isinstance(payload, dict):
            raise TmapClientError()
        return payload

    def close(self) -> None:
        if self._owns_http_client:
            self.http_client.close()
