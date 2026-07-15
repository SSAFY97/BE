from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.chat import router as chat_router
from app.api.locations import router as locations_router
from app.api.posts import router as posts_router
from app.core.database import init_db
from app.core.response import build_response

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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=build_response(422, "요청 데이터가 올바르지 않습니다.", None))


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=build_response(500, "서버 내부 오류가 발생했습니다.", None))


@app.get("/health")
def health_check() -> dict[str, object]:
    return build_response(200, "서버 상태가 정상입니다.", {"status": "ok"})


init_db()
