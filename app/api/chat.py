from fastapi import APIRouter

from app.core.response import CommonResponse, build_response
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=CommonResponse[ChatResponse])
def chat(request: ChatRequest) -> dict[str, object]:
    service = ChatService()
    payload = service.ask(request)
    return build_response(200, "챗봇 응답에 성공했습니다.", payload.model_dump())
