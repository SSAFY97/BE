# LocalHub Backend Instructions

## 1. Project Context

This repository implements the LocalHub backend for an SSAFY team project.

LocalHub is a Seoul regional information sharing service based on provided public-data JSON files.

The backend must satisfy the approved RFB and MVP requirements.

The RFB and approved API specification are the source of truth.

Do not add, remove, or reinterpret requirements without an explicit user request.

Prefer the simplest implementation that satisfies the MVP.

Do not over-engineer for hypothetical future requirements.

Do not perform unrelated refactoring while implementing a feature.


## 2. Required Technology Stack

Use the following technologies:

- Python
- FastAPI
- SQLAlchemy ORM
- SQLite
- OpenAI API
- Render for backend deployment

Do not replace the required framework, ORM, or database.

Do not introduce another database such as PostgreSQL or MySQL.

Do not introduce Redis, Kafka, Celery, Elasticsearch, or other infrastructure unless explicitly requested.

Do not add a new production dependency unless it is necessary for the requested feature.

When adding a dependency:

1. Explain why the existing stack cannot reasonably solve the problem.
2. Explain the benefit of the selected dependency.
3. Mention at least one reasonable alternative.


## 3. MVP Scope

The backend MVP contains only the following domains:

1. Seoul regional information
2. Anonymous community posts
3. Regional information chatbot

Selected optional community features:

- Post search
- Post view count
- Post likes

Do not implement the following unless explicitly requested:

- User registration
- Login
- JWT authentication
- OAuth
- Role or permission systems
- Comments
- Bookmarking
- Image upload
- WebSocket notifications
- Chat rooms
- Chat message persistence
- Redis caching
- Admin APIs


## 4. Architecture

Use the following dependency direction:

Router
-> Service
-> Repository
-> SQLAlchemy
-> SQLite

Recommended project structure:

app/
├── main.py
├── api/
│   ├── posts.py
│   ├── locations.py
│   └── chat.py
├── models/
│   └── post.py
├── schemas/
│   ├── common.py
│   ├── post.py
│   ├── location.py
│   └── chat.py
├── services/
│   ├── post_service.py
│   ├── location_service.py
│   └── chat_service.py
├── repositories/
│   └── post_repository.py
├── core/
│   ├── config.py
│   └── database.py
└── data/
    └── seoul.json

Keep responsibilities separated.

Router:
- Handles HTTP request and response concerns.
- Performs FastAPI dependency injection.
- Does not contain database queries.
- Does not contain OpenAI prompt construction.

Service:
- Contains application and business logic.
- Coordinates repositories and other services.

Repository:
- Contains SQLAlchemy database access logic.
- Does not contain HTTP-specific logic.

Do not create abstractions that have only one trivial implementation unless they provide a clear separation of responsibility.


## 5. Common API Response Format

All application APIs must use the following common response structure.

Success response:

```json
{
  "response": 200,
  "message": "요청에 성공했습니다.",
  "data": {}
}
```

Fields:

- `response`: HTTP status code represented as an integer.
- `message`: Human-readable Korean response message.
- `data`: Actual response payload or `null`.

The `response` field must match the actual HTTP status code.

Use Korean messages consistently.

Do not return raw ORM models, dictionaries, lists, primitive values, or FastAPI default error structures directly from application endpoints.

All success and error responses must follow:

```json
{
  "response": 200,
  "message": "요청에 성공했습니다.",
  "data": {}
}
```

Allowed field names:

- `response`
- `message`
- `data`

Do not replace these fields with:

- `status`
- `statusCode`
- `code`
- `result`
- `detail`
- `error`


## 6. Common Response Implementation

Implement a reusable generic common response schema.

Recommended concept:

```python
class CommonResponse(BaseModel, Generic[T]):
    response: int
    message: str
    data: T | None = None
```

Use the Pydantic generic model pattern supported by the Pydantic version installed in the project.

Do not manually duplicate `response`, `message`, and `data` in every response schema.

Do not create an unnecessarily complex response factory, response hierarchy, or abstract base class.

A simple `CommonResponse[T]` generic schema is preferred for this MVP.

Use `response_model=CommonResponse[SpecificResponse]` when practical.


## 7. Error Response Format

Error responses must use the same common response structure.

Not found:

```json
{
  "response": 404,
  "message": "게시글을 찾을 수 없습니다.",
  "data": null
}
```

Password mismatch:

```json
{
  "response": 403,
  "message": "비밀번호가 일치하지 않습니다.",
  "data": null
}
```

Validation failure:

```json
{
  "response": 422,
  "message": "요청 데이터가 올바르지 않습니다.",
  "data": null
}
```

Internal server error:

```json
{
  "response": 500,
  "message": "서버 내부 오류가 발생했습니다.",
  "data": null
}
```

Register FastAPI exception handlers so that:

- `HTTPException`
- Request validation errors
- Unhandled internal errors

are converted to the common API response format.

Do not expose FastAPI's default response:

```json
{
  "detail": "..."
}
```

Do not expose:

- Stack traces
- SQLAlchemy error messages
- SQLite error messages
- OpenAI API error details
- Secret values

through the client response message.


## 8. Regional Information Data

The provided Seoul JSON file is the source of truth for regional information.

Do not directly call external public-data APIs.

Do not scrape external websites.

Do not migrate Seoul regional data into SQLite unless explicitly requested.

Regional information should be loaded and searched through `LocationService`.

Treat the provided JSON data as read-only.

Supported regional information categories are based on the actual provided JSON dataset.

Do not invent fields that are not present in the JSON data.

Before implementing location APIs:

1. Inspect the actual JSON schema.
2. Identify common and category-specific fields.
3. Design response schemas based on the real data.

Never assume latitude, longitude, date, or address fields exist without inspecting the dataset.


## 9. Community Post Model

Community posts are anonymous.

Do not implement user authentication.

The `posts` table contains:

- `id`
- `title`
- `content`
- `writer`
- `password`
- `view_count`
- `like_count`
- `created_at`
- `updated_at`

Recommended schema:

| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| title | VARCHAR(200) | Post title |
| content | TEXT | Post content |
| writer | VARCHAR(100) | Anonymous writer name |
| password | VARCHAR(100) | Password used for modification and deletion |
| view_count | INTEGER | Post view count |
| like_count | INTEGER | Post like count |
| created_at | DATETIME | Created timestamp |
| updated_at | DATETIME | Updated timestamp |

`writer` is a display name entered by the anonymous user.

`writer` does not represent an authenticated user.

Do not create a users table or foreign key for `writer`.

The password is used only to authorize post modification and deletion.

According to the project RFB, the post password is intentionally stored and compared as plain text for educational purposes.

Do not replace this behavior with password hashing unless explicitly requested.

However:

- Never include `password` in an API response.
- Never log password values.
- Never expose password through exception messages.
- Never intentionally include password in repr or debug output.

Password mismatch must return HTTP 403.

Missing posts must return HTTP 404.


## 10. Post Validation Rules

Apply request validation at the API boundary.

Recommended rules:

- `title`: 1 to 200 characters
- `content`: at least 1 character
- `writer`: 1 to 100 characters
- `password`: 4 to 100 characters
- `page`: minimum 1
- `size`: minimum 1

Do not silently truncate invalid values.

Return the common 422 response format for validation failures.


## 11. API Contract

Preserve the following API contract unless an explicit requirement change is requested.

### Regional Information

#### GET /api/locations

Query parameters:

- `category`: optional
- `keyword`: optional
- `limit`: optional

Example response:

```json
{
  "response": 200,
  "message": "지역 정보 목록 조회에 성공했습니다.",
  "data": {
    "items": [],
    "total": 0
  }
}
```

#### GET /api/locations/{location_id}

Example response:

```json
{
  "response": 200,
  "message": "지역 정보 조회에 성공했습니다.",
  "data": {
    "id": "location-001",
    "name": "지역 정보명"
  }
}
```


### Community Posts

#### GET /api/posts

Query parameters:

- `page`: default 1
- `size`: default 10
- `keyword`: optional

Search `title` and `content` when `keyword` is provided.

Example response:

```json
{
  "response": 200,
  "message": "게시글 목록 조회에 성공했습니다.",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "서울 축제 후기",
        "writer": "익명여행자",
        "view_count": 10,
        "like_count": 2,
        "created_at": "2026-07-15T10:30:00"
      }
    ],
    "page": 1,
    "size": 10,
    "total": 1,
    "total_pages": 1
  }
}
```

Do not include `password` in list responses.


#### GET /api/posts/{post_id}

The detail API increments the post view count.

Example response:

```json
{
  "response": 200,
  "message": "게시글 조회에 성공했습니다.",
  "data": {
    "id": 1,
    "title": "서울 축제 후기",
    "content": "축제에 다녀왔습니다.",
    "writer": "익명여행자",
    "view_count": 11,
    "like_count": 2,
    "created_at": "2026-07-15T10:30:00",
    "updated_at": "2026-07-15T10:30:00"
  }
}
```

Never include `password` in the response.


#### POST /api/posts

Request:

```json
{
  "title": "서울 맛집 추천합니다",
  "content": "서울역 근처 맛집 추천합니다.",
  "writer": "서울러",
  "password": "1234"
}
```

Example response:

```json
{
  "response": 201,
  "message": "게시글 작성에 성공했습니다.",
  "data": {
    "id": 1,
    "title": "서울 맛집 추천합니다",
    "content": "서울역 근처 맛집 추천합니다.",
    "writer": "서울러",
    "view_count": 0,
    "like_count": 0,
    "created_at": "2026-07-15T11:00:00",
    "updated_at": "2026-07-15T11:00:00"
  }
}
```


#### PUT /api/posts/{post_id}

Request:

```json
{
  "title": "서울 맛집 추천 수정",
  "content": "내용을 수정했습니다.",
  "writer": "서울러",
  "password": "1234"
}
```

The request password is compared with the stored password.

Only update the post when the password matches.

Example response:

```json
{
  "response": 200,
  "message": "게시글 수정에 성공했습니다.",
  "data": {
    "id": 1,
    "title": "서울 맛집 추천 수정",
    "content": "내용을 수정했습니다.",
    "writer": "서울러",
    "view_count": 0,
    "like_count": 0,
    "created_at": "2026-07-15T11:00:00",
    "updated_at": "2026-07-15T11:30:00"
  }
}
```


#### DELETE /api/posts/{post_id}

Request:

```json
{
  "password": "1234"
}
```

Example response:

```json
{
  "response": 200,
  "message": "게시글 삭제에 성공했습니다.",
  "data": null
}
```


#### POST /api/posts/{post_id}/likes

The request body is empty.

Increment the post like count.

Example response:

```json
{
  "response": 200,
  "message": "게시글 좋아요에 성공했습니다.",
  "data": {
    "post_id": 1,
    "like_count": 3
  }
}
```

The backend does not track user-specific duplicate likes because the service has no authenticated user identity.

Do not create a `post_likes` table for this MVP unless explicitly requested.


### Chatbot

#### POST /api/chat

Request:

```json
{
  "message": "이번 주 서울에서 갈 만한 축제 추천해줘"
}
```

Example response:

```json
{
  "response": 200,
  "message": "챗봇 응답 생성에 성공했습니다.",
  "data": {
    "answer": "이번 주 서울에서 진행되는 축제를 안내해드릴게요.",
    "references": [
      {
        "type": "location",
        "id": "festival-001",
        "name": "서울 문화 축제"
      }
    ]
  }
}
```


### Health Check

#### GET /health

Example response:

```json
{
  "response": 200,
  "message": "서버가 정상적으로 동작 중입니다.",
  "data": {
    "status": "ok"
  }
}
```


## 12. View Count and Like Count

Prefer database-side increment operations.

Avoid the following read-modify-write pattern when incrementing counters:

```python
post.view_count += 1
```

Prefer an atomic database update equivalent to:

```sql
UPDATE posts
SET view_count = view_count + 1
WHERE id = :post_id;
```

Apply the same principle to `like_count`.

Do not introduce distributed locking or Redis for counters.


## 13. Chatbot Rules

`POST /api/chat` must answer questions using:

1. Provided Seoul regional JSON data.
2. Community post data stored in SQLite.

The chatbot must be grounded in retrieved project data.

Recommended flow:

User Question
-> Retrieve relevant Seoul JSON data
-> Retrieve relevant community posts when necessary
-> Build context
-> Call OpenAI API
-> Return answer and references

Do not send the entire Seoul JSON dataset to the OpenAI API for every request.

Retrieve a small set of relevant records first.

Do not allow the model to present unsupported regional information as confirmed fact.

The system prompt must instruct the model to state that the information cannot be confirmed from the provided Seoul data when relevant information is unavailable.

Chat history is managed by the frontend.

Do not create `chat_rooms` or `chat_messages` tables.

Do not persist conversation history in SQLite unless explicitly requested.


## 14. Environment and Security

All sensitive values must be managed through environment variables.

Examples:

- `OPENAI_API_KEY`
- `DATABASE_URL`
- Database path
- External service credentials

Use `.env` for local development.

`.env` must be included in `.gitignore`.

Never hard-code API keys.

Never commit secrets.

Provide `.env.example` containing variable names only.

Example:

```env
OPENAI_API_KEY=
DATABASE_URL=
```

Do not include real secret values in:

- Source code
- README
- Tests
- Logs
- Example requests


## 15. FastAPI and Schema Rules

Use Pydantic request and response schemas.

Define `response_model` when practical.

Do not return SQLAlchemy ORM models directly without an appropriate response schema.

Validate input at the API boundary.

Use clear HTTP status codes.

Use `HTTPException` or centralized application exceptions consistently, but ensure final client responses are converted to the common API response structure.

Avoid broad exception handling such as:

```python
except Exception:
    return ...
```

Do not silently swallow exceptions.

Do not expose internal stack traces or OpenAI API errors directly to clients.


## 16. Coding Style

Prefer clear and readable Python code.

Use:

- `snake_case` for functions and variables
- `PascalCase` for classes
- Explicit type hints
- Small functions with clear responsibilities

Avoid unnecessary comments that only repeat the code.

Comments should explain:

- Why a non-obvious decision was made.
- An intentional MVP limitation.
- Behavior required specifically by the RFB.

Do not create generic utility classes without a concrete use case.

Avoid premature abstraction.


## 17. Change Workflow

Before modifying code:

1. Inspect the related files.
2. Identify the current implementation and project structure.
3. Confirm the requested change against the RFB and MVP scope.
4. Identify affected APIs, schemas, services, repositories, and tests.
5. Plan the smallest reasonable change.

Do not immediately rewrite working code.

Do not perform unrelated refactoring while implementing a feature.

When an existing design conflicts with the requested feature:

1. Explain the conflict.
2. Present reasonable alternatives.
3. Compare their advantages and disadvantages.
4. Select the smallest solution that satisfies the MVP.


## 18. Verification

After making a change:

1. Run relevant tests.
2. Check application startup.
3. Verify affected API behavior.
4. Review the diff for unrelated changes.
5. Check that passwords are not exposed.
6. Check that secrets are not committed.
7. Confirm that the API contract has not changed unintentionally.
8. Confirm that success and error responses follow the common response format.

For API changes, verify at least:

- Normal request
- Resource not found
- Validation failure
- Password mismatch when applicable

Do not claim a test passed unless the test command was actually executed.


## 19. Decision Rationale

For a non-trivial technical decision, record:

- Problem
- Considered Options
- Selected Option
- Reason for Selection
- Advantages
- Disadvantages
- MVP Trade-off

Example:

### Problem

Post view counts may lose increments under concurrent requests.

### Considered Options

1. ORM entity read-modify-write
2. Atomic SQL UPDATE
3. Redis counter

### Selected Option

Atomic SQL UPDATE

### Reason for Selection

It avoids the read-modify-write lost update pattern while remaining within the current SQLite architecture.

### Advantages

- Simple
- No additional infrastructure
- Appropriate for MVP

### Disadvantages

- Limited compared with distributed counter architectures

### MVP Trade-off

Redis was rejected because distributed counter scalability is outside the project scope.


## 20. Final Response Format

After completing a coding task, summarize:

1. Changed files
2. Implemented behavior
3. Technical decisions and rationale
4. Alternatives considered
5. Tests or verification actually performed
6. Remaining limitations or risks

Clearly distinguish:

- Verified facts
- Assumptions
- Work not performed

Never state that code was tested if tests were not run.
