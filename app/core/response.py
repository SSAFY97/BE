from typing import Any


def build_response(status_code: int, message: str, data: Any = None) -> dict[str, Any]:
    return {"response": status_code, "message": message, "data": data}
