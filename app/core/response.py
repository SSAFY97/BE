from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class CommonResponse(BaseModel, Generic[T]):
    response: int
    message: str
    data: T | None = None


def build_response(status_code: int, message: str, data: Any = None) -> dict[str, Any]:
    return {"response": status_code, "message": message, "data": data}
