import re
from typing import Any

from fastapi import HTTPException
from openai import APIStatusError, OpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_MODEL
from app.core.database import SessionLocal
from app.repositories.post_repository import PostRepository
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.location_service import LocationService


CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "관광지": ("관광", "관광지", "명소"),
    "레포츠": ("레포츠", "스포츠", "액티비티", "운동", "체험"),
    "문화시설": ("문화", "문화시설", "전시", "박물관", "미술관", "공연장"),
    "쇼핑": ("쇼핑", "시장", "백화점", "몰", "상점"),
    "숙박": ("숙박", "숙소", "호텔", "게스트하우스", "펜션"),
    "여행코스": ("코스", "여행코스", "일정", "데이트코스", "동선"),
    "축제공연행사": ("축제", "공연", "행사", "페스티벌", "이벤트"),
}
GENERIC_RECOMMENDATION_KEYWORDS = ("가볼", "유명", "추천", "여행")


class ChatService:
    def __init__(self) -> None:
        self.location_service = LocationService()
        self.session = SessionLocal()
        self.post_repository = PostRepository(self.session)

    def close(self) -> None:
        self.session.close()

    def _extract_keywords(self, message: str) -> list[str]:
        words = re.findall(r"[0-9A-Za-z가-힣]+", message.lower())
        stopwords = {
            "서울",
            "서울에서",
            "가장",
            "추천",
            "추천해줘",
            "알려줘",
            "어디",
            "좋은",
            "유명한",
            "유명",
            "장소",
            "곳",
        }
        keywords: list[str] = []

        for word in words:
            normalized = word.removesuffix("에서").removesuffix("으로").removesuffix("로")
            if len(normalized) < 2 or normalized in stopwords:
                continue
            if normalized not in keywords:
                keywords.append(normalized)

        return keywords

    def _extract_categories(self, message: str) -> list[str]:
        categories: list[str] = []
        for category, keywords in CATEGORY_KEYWORDS.items():
            if category == "관광지":
                continue
            if any(keyword in message for keyword in keywords):
                categories.append(category)

        tourism_keywords = CATEGORY_KEYWORDS["관광지"]
        if any(keyword in message for keyword in tourism_keywords):
            categories.append("관광지")
        elif not categories and any(keyword in message for keyword in GENERIC_RECOMMENDATION_KEYWORDS):
            categories.append("관광지")

        return categories

    def _find_locations(self, message: str, limit: int = 5) -> list[Any]:
        matched: list[Any] = []
        seen_ids: set[str] = set()

        for keyword in self._extract_keywords(message):
            locations = self.location_service.get_locations(keyword=keyword, limit=limit)
            for item in locations.items:
                if item.id not in seen_ids:
                    matched.append(item)
                    seen_ids.add(item.id)
                if len(matched) >= limit:
                    return matched

        for category in self._extract_categories(message):
            if len(matched) >= limit:
                break
            locations = self.location_service.get_locations(category=category, limit=limit)
            for item in locations.items:
                if item.id not in seen_ids:
                    matched.append(item)
                    seen_ids.add(item.id)
                if len(matched) >= limit:
                    break

        return matched[:limit]

    def _find_posts(self, message: str, limit: int = 5) -> list[Any]:
        matched: list[Any] = []
        seen_ids: set[int] = set()

        for keyword in self._extract_keywords(message):
            posts = self.post_repository.list(page=1, size=limit, keyword=keyword)[0]
            for post in posts:
                if post.id not in seen_ids:
                    matched.append(post)
                    seen_ids.add(post.id)
                if len(matched) >= limit:
                    return matched

        return matched[:limit]

    def _build_context(self, message: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        locations = self._find_locations(message)
        posts = self._find_posts(message)

        location_context = [
            {
                "id": item.id,
                "title": item.title,
                "category": item.category,
                "address": item.address,
            }
            for item in locations
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
                answer="OpenAI API 키가 설정되지 않아 답변을 생성할 수 없습니다.",
                references=[],
            )

        location_context, post_context = self._build_context(request.message)
        client = OpenAI(api_key=OPENAI_API_KEY)
        prompt = (
            "당신은 서울 지역 정보와 익명 커뮤니티 게시글을 기반으로 답하는 챗봇입니다. "
            "제공된 데이터에 근거해서만 답변하고, 확인할 수 없는 정보는 "
            "'제공된 데이터로는 확인할 수 없습니다'라고 말하세요.\n"
            f"사용자 질문: {request.message}\n"
            f"지역 정보: {location_context}\n"
            f"게시글: {post_context}\n"
            "답변은 한국어로 짧고 명확하게 작성하고, 참고한 항목을 간단히 포함하세요.\n"
            "친절한 말투를 기반으로 답변하고, ~는 어떠신가요 같은 표현으로 답변해주세요."
        )

        try:
            response = client.responses.create(
                model=OPENAI_MODEL,
                input=prompt,
            )
        except APIStatusError as exc:
            if exc.status_code in {403, 404}:
                raise HTTPException(
                    status_code=502,
                    detail=(
                        f"OpenAI 모델 '{OPENAI_MODEL}'에 접근할 수 없습니다. "
                        "OPENAI_MODEL 값을 현재 프로젝트에서 사용 가능한 모델로 변경해주세요."
                    ),
                ) from exc
            raise

        answer = response.output_text
        references = [
            {"type": "location", "id": item["id"], "title": item["title"]}
            for item in location_context[:3]
        ] + [
            {"type": "post", "id": str(item["id"]), "title": item["title"]}
            for item in post_context[:3]
        ]
        return ChatResponse(answer=answer, references=references)
