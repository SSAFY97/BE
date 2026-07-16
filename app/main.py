from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.chat import router as chat_router
from app.api.locations import router as locations_router
from app.api.posts import router as posts_router
from app.api.routes import router as routes_router
from app.core.database import init_db
from app.core.response import CommonResponse, build_response

app = FastAPI(title="LocalHub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(posts_router, prefix="/api")
app.include_router(locations_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(routes_router, prefix="/api")


def _validation_error_message(exc: RequestValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "요청 데이터가 올바르지 않습니다."

    error = errors[0]
    loc = tuple(error.get("loc", ()))
    field = loc[-1] if loc else None
    error_type = str(error.get("type", ""))

    if "password" in loc:
        return "비밀번호가 올바르지 않습니다."

    if field == "page":
        return "페이지 번호는 1 이상이어야 합니다."
    if field in ("size", "limit"):
        return "조회 개수는 1 이상이어야 합니다."

    if field == "latitude":
        prefix = "출발지" if "origin" in loc else "도착지" if "destination" in loc else ""
        return f"{prefix} 위도는 -90 이상 90 이하로 입력해주세요.".strip()
    if field == "longitude":
        prefix = "출발지" if "origin" in loc else "도착지" if "destination" in loc else ""
        return f"{prefix} 경도는 -180 이상 180 이하로 입력해주세요.".strip()

    if error_type == "missing":
        field_messages = {
            "title": "제목을 입력해주세요.",
            "content": "내용을 입력해주세요.",
            "writer": "작성자를 입력해주세요.",
            "message": "메시지를 입력해주세요.",
            "origin": "출발지를 입력해주세요.",
            "destination": "도착지를 입력해주세요.",
        }
        if isinstance(field, str) and field in field_messages:
            return field_messages[field]
        return "필수 입력값이 누락되었습니다."

    field_messages = {
        "title": "제목이 올바르지 않습니다.",
        "content": "내용이 올바르지 않습니다.",
        "writer": "작성자가 올바르지 않습니다.",
        "message": "메시지가 올바르지 않습니다.",
        "name": "장소명이 올바르지 않습니다.",
    }
    if isinstance(field, str) and field in field_messages:
        return field_messages[field]

    return "요청 데이터가 올바르지 않습니다."


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_response(422, _validation_error_message(exc), None),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else "요청을 처리할 수 없습니다."
    return JSONResponse(
        status_code=exc.status_code,
        content=build_response(exc.status_code, message, None),
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=build_response(500, "서버 내부 오류가 발생했습니다.", None),
    )


@app.get("/health", response_model=CommonResponse[dict[str, str]])
def health_check() -> dict[str, object]:
    return build_response(200, "서버 상태가 정상입니다.", {"status": "ok"})


init_db()
