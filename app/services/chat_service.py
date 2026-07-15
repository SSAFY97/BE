import os
from typing import Any

from openai import OpenAI

from app.core.config import OPENAI_API_KEY
from app.repositories.post_repository import PostRepository
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.location_service import LocationService
from app.core.database import SessionLocal


class ChatService:
    def __init__(self) -> None:
        self.location_service = LocationService()
        self.session = SessionLocal()
        self.post_repository = PostRepository(self.session)

    def _build_context(self, message: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        locations = self.location_service.get_locations(keyword=message, limit=5)
        posts = self.post_repository.list(page=1, size=5, keyword=message)[0]

        location_context = [
            {
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "address": item.address,
            }
            for item in locations.items
        ]
        post_context = [
            {
                "id": post.id,
                "title": post.title,
                "content": post.content,
            }
            for post in posts
        ]
        return location_context, post_context

    def ask(self, request: ChatRequest) -> ChatResponse:
        if not OPENAI_API_KEY:
            return ChatResponse(
                answer="OpenAI API 키가 설정되지 않아 답변을 생성할 수 없습니다. 제공된 지역 데이터만 기반으로 간단히 안내하겠습니다.",
                references=[],
            )

        location_context, post_context = self._build_context(request.message)
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = (
            "당신은 서울 지역 정보와 익명 커뮤니티 게시글을 기반으로 답하는 챗봇입니다. "
            "제공된 데이터에 없거나 확인할 수 없는 정보는 반드시 '제공된 데이터로는 확인할 수 없습니다'라고 말하세요.\n"
            f"사용자 질문: {request.message}\n"
            f"지역 정보: {location_context}\n"
            f"게시글: {post_context}\n"
            "답변은 한국어로 짧고 명확하게 작성하고, 참고한 항목을 간단히 포함하세요."
        )

        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )
        answer = response.output_text
        references = [
            {"type": "location", "id": item["id"], "title": item["title"]}
            for item in location_context[:3]
        ] + [
            {"type": "post", "id": str(item["id"]), "title": item["title"]}
            for item in post_context[:3]
        ]
        return ChatResponse(answer=answer, references=references)
