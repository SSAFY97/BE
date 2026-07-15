# LocalHub FastAPI Backend Copilot Instructions

## 1. Project Overview

Project Name:
LocalHub

Purpose:
공공데이터 기반 지역 정보 공유 커뮤니티 서비스

Backend Role:
FastAPI 기반 REST API 서버 구축

Main Features:
- 서울 권역 JSON 데이터 기반 지역 정보 제공
- 익명 커뮤니티 CRUD
- 비밀번호 기반 게시글 수정/삭제
- OpenAI 기반 지역정보 챗봇 API
- SQLite 데이터 저장
- 배포 가능한 Backend API 제공


---

# 2. Technology Stack

Backend Framework:
- FastAPI

Language:
- Python 3.11+

Database:
- SQLite

ORM:
- SQLAlchemy 2.x

Migration:
- Alembic (선택)

Validation:
- Pydantic v2

Server:
- Uvicorn

Environment:
- dotenv (.env)

Deployment:
- Render


---

# 3. Development Rules

## General Rules

- 모든 코드는 Python PEP8 스타일 준수
- 함수명은 snake_case 사용
- 클래스명은 PascalCase 사용
- 타입 힌트 필수 적용
- 비즈니스 로직과 API Router 로직 분리
- 하나의 파일에 모든 코드를 작성하지 않는다


Example:

Good:
```python
def get_post(post_id: int) -> Post:
    pass

Bad:

def getPost(id):
    pass
4. Backend Architecture

프로젝트 구조는 아래 형태를 따른다.

backend/

├── app/
│
├── main.py
│
├── database/
│   ├── connection.py
│   └── session.py
│
├── models/
│   └── post.py
│
├── schemas/
│   └── post.py
│
├── routers/
│   ├── posts.py
│   ├── chat.py
│   └── locations.py
│
├── services/
│   ├── post_service.py
│   └── chat_service.py
│
├── repositories/
│   └── post_repository.py
│
├── data/
│   └── seoul.json
│
├── core/
│   └── config.py
│
└── utils/

requirements.txt
.env
.gitignore

5. Database Rules

Database:
SQLite 사용

SQLAlchemy ORM 필수 적용

주요 테이블:

posts

게시글 정보 저장

Columns:

id
title
content
password
view_count
like_count
created_at
updated_at

Requirements:

게시글은 반드시 DB 저장
JSON 파일에 게시글 저장 금지
ORM 기반 CRUD 구현
6. Community API Requirements
Post API

Base URL:

/api/posts

Required APIs:

게시글 목록 조회

GET

/api/posts

Response:

게시글 목록
조회수 포함
게시글 상세 조회

GET

/api/posts/{post_id}

Requirement:

조회 시 view_count 증가
게시글 작성

POST

/api/posts

Request:

{
"title":"",
"content":"",
"password":""
}

Rules:

회원가입 없음
로그인 없음
비밀번호 기반 인증
게시글 수정

PUT

/api/posts/{post_id}

Rules:

입력 password 비교
일치 시 수정 가능
게시글 삭제

DELETE

/api/posts/{post_id}

Rules:

입력 password 검증
일치 시 삭제
7. Search Feature

Optional Feature:
게시글 검색

Implementation:

Query Parameter 사용

Example:

GET /api/posts?keyword=서울

검색 대상:

title
content
8. Like Feature

Optional Feature:
좋아요

Implementation:

단순 카운트 증가 방식

API:

POST

/api/posts/{post_id}/like

Response:

{
"like_count":10
}
9. JSON Data Handling

Provided Data:

서울 권역 JSON

Location:

app/data/seoul.json

Rules:

JSON 원본 데이터 수정 금지
Service Layer에서 데이터 조회
Router에서 직접 JSON 접근 금지

Example:

Router

↓

Service

↓

JSON Repository

구조 유지

10. Chatbot API

Required API:

POST

/api/chat

Purpose:

서울 지역 정보 질의응답

Request:

{
"message":"서울 축제 추천해줘"
}

Response:

{
"answer":"..."
}

Implementation:

OpenAI API 활용 가능
API Key는 반드시 환경변수 사용
코드 내부 Key 작성 금지
11. Environment Rules

절대 금지:

OPENAI_API_KEY="xxxxx"

사용:

.env

OPENAI_API_KEY=
DATABASE_URL=

config.py에서 관리

Example:

from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY=os.getenv(
"OPENAI_API_KEY"
)
12. Security Rules

Must:

.env 파일 Git 제외
Secret Key 코드 작성 금지
API Key 노출 금지

.gitignore:

.env
__pycache__/
*.db
13. Error Handling

모든 API는 HTTP Exception 처리

Example:

raise HTTPException(
status_code=404,
detail="Post not found"
)
14. API Documentation

FastAPI 기본 Swagger 유지

접속:

/docs

모든 Endpoint:

summary 작성
response model 작성
status code 명시
15. Testing Rules

가능하면 pytest 작성

중요 테스트:

게시글 생성
게시글 조회
수정 비밀번호 검증
삭제 비밀번호 검증
검색 기능
좋아요 증가
16. Git Rules

Commit Convention:

feat:
fix:
refactor:
docs:
test:

Example:

feat: add post CRUD API
fix: resolve password validation error
17. Copilot Agent Behavior Rules

Copilot Agent는 다음 순서로 작업한다.

기존 프로젝트 구조 확인
요구사항 분석
필요한 파일 생성
DB 모델 작성
Schema 작성
Repository 작성
Service 작성
Router 작성
테스트 작성
실행 오류 확인

코드 작성 전:

기존 코드 영향 분석
중복 코드 확인
필요한 의존성 확인

코드 작성 후:

import 오류 확인
FastAPI 실행 가능 여부 확인
Swagger 등록 확인
18. MVP Scope Control

현재 MVP 범위:

Must Have:

YES

JSON 데이터 연동
CRUD
Chat API
SQLite
FastAPI
배포 준비

Should Have:

YES

게시글 검색
조회수
좋아요

제외:

NO

WebSocket
지도 API
날씨 API
경로 안내

불필요한 기능 추가 금지.

Final Goal

완성 목표:

"서울 공공데이터 기반 익명 지역 커뮤니티 + AI 지역정보 챗봇 서비스를 제공하는 안정적인 FastAPI REST API 서버 구축"

Copilot Agent는 항상 MVP 범위와 RFP 요구사항을 우선하여 개발한다.