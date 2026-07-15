# LocalHub Project Instructions

## 1. Project Context

This repository implements the LocalHub backend for an SSAFY team project.

LocalHub is a Seoul regional information sharing service based on provided public-data JSON files.

The backend must satisfy the approved RFB and MVP requirements.

The RFB and approved API specification are the source of truth.

Do not add, remove, or reinterpret requirements without an explicit user request.

Prefer the simplest implementation that satisfies the MVP.
Do not over-engineer for hypothetical future requirements.


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


## 5. Regional Information Data

The provided Seoul JSON file is the source of truth for regional information.

Do not directly call external public-data APIs.

Do not scrape external websites.

Do not migrate Seoul regional data into SQLite unless explicitly requested.

Regional information should be loaded and searched through LocationService.

Treat the provided JSON data as read-only.

Supported regional information categories are based on the actual provided JSON dataset.

Do not invent fields that are not present in the JSON data.

Before implementing location APIs:
1. Inspect the actual JSON schema.
2. Identify common and category-specific fields.
3. Design response schemas based on the real data.

Never assume latitude, longitude, date, or address fields exist without inspecting the dataset.


## 6. Community Post Rules

Community posts are anonymous.

Do not implement user authentication.

A post contains:

- id
- title
- content
- password
- view_count
- like_count
- created_at
- updated_at

The password is used only to authorize post modification and deletion.

According to the project RFB, the post password is intentionally stored and compared as plain text for educational purposes.

Do not replace this behavior with password hashing unless explicitly requested.

However:

- Never include password in an API response.
- Never log password values.
- Never expose password through exception messages.
- Never include password in repr or debug output intentionally.

Password mismatch must return HTTP 403.

Missing posts must return HTTP 404.


## 7. API Contract

Preserve the following API contract.

### Regional information

GET /api/locations

Query parameters:

- category: optional
- keyword: optional
- limit: optional

GET /api/locations/{location_id}


### Community posts

GET /api/posts

Query parameters:

- page: default 1
- size: default 10
- keyword: optional

Search the title and content when keyword is provided.

GET /api/posts/{post_id}

The detail API increments the post view count.

POST /api/posts

Request:

{
  "title": "string",
  "content": "string",
  "password": "string"
}

PUT /api/posts/{post_id}

Request:

{
  "title": "string",
  "content": "string",
  "password": "string"
}

DELETE /api/posts/{post_id}

Request:

{
  "password": "string"
}

POST /api/posts/{post_id}/likes

Increment the post like count.

The backend does not track user-specific duplicate likes because the service has no user identity.


### Chatbot

POST /api/chat

Request:

{
  "message": "string"
}

Response:

{
  "answer": "string",
  "references": []
}


### Health Check

GET /health

Response:

{
  "status": "ok"
}


## 8. View Count and Like Count

Prefer database-side increment operations.

Avoid the following read-modify-write pattern when incrementing counters:

post.view_count += 1

Prefer an atomic database update equivalent to:

UPDATE posts
SET view_count = view_count + 1
WHERE id = :post_id;

Apply the same principle to like_count.

Do not introduce distributed locking or Redis for counters.


## 9. Chatbot Rules

POST /api/chat must answer questions using:

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

The system prompt must instruct the model to say that the information cannot be confirmed from the provided Seoul data when relevant information is unavailable.

Chat history is managed by the frontend.

Do not create chat_rooms or chat_messages tables.

Do not persist conversation history in SQLite unless explicitly requested.


## 10. Environment and Security

All sensitive values must be managed through environment variables.

Examples:

- OPENAI_API_KEY
- DATABASE_URL or database path
- External service credentials

Use .env for local development.

.env must be included in .gitignore.

Never hard-code API keys.

Never commit secrets.

Provide .env.example containing variable names only.

Example:

OPENAI_API_KEY=
DATABASE_URL=

Do not include real secret values in:

- Source code
- README
- Tests
- Logs
- Example requests


## 11. FastAPI and Schema Rules

Use Pydantic request and response schemas.

Define response_model when practical.

Do not return SQLAlchemy ORM models directly without an appropriate response schema.

Validate input at the API boundary.

Use clear HTTP status codes.

Use HTTPException or centralized exception handling consistently.

Avoid broad exception handling such as:

except Exception:
    return ...

Do not silently swallow exceptions.

Do not expose internal stack traces or OpenAI API errors directly to clients.


## 12. Coding Style

Prefer clear and readable Python code.

Use:

- snake_case for functions and variables
- PascalCase for classes
- Explicit type hints
- Small functions with clear responsibilities

Avoid unnecessary comments that only repeat the code.

Comments should explain:

- Why a non-obvious decision was made.
- An intentional MVP limitation.
- Behavior required specifically by the RFB.

Do not create generic utility classes without a concrete use case.

Avoid premature abstraction.


## 13. Change Workflow

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


## 14. Verification

After making a change:

1. Run relevant tests.
2. Check application startup.
3. Verify affected API behavior.
4. Review the diff for unrelated changes.
5. Check that passwords are not exposed.
6. Check that secrets are not committed.
7. Confirm that the API contract has not changed unintentionally.

For API changes, verify at least:

- Normal request
- Resource not found
- Validation failure
- Password mismatch when applicable

Do not claim a test passed unless the test command was actually executed.


## 15. Decision Rationale

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

It prevents the read-modify-write lost update pattern while remaining within the existing SQLite architecture.

### Advantages

- Simple
- No additional infrastructure
- Appropriate for MVP

### Disadvantages

- Limited compared with distributed counter architectures

### MVP Trade-off

Redis was rejected because distributed counter scalability is outside the project scope.


## 16. Final Response Format

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

## Common API Response Format

All application APIs must use the following common response structure.

Success response:

{
  "response": 200,
  "message": "요청에 성공했습니다.",
  "data": {}
}

Fields:

- response: HTTP status code represented as an integer.
- message: Human-readable Korean response message.
- data: Actual response payload.

Do not return raw ORM models, dictionaries, lists, or primitive values directly from API endpoints.

All API responses must be wrapped in the common response structure.

Example:

{
  "response": 200,
  "message": "게시글 조회에 성공했습니다.",
  "data": {
    "id": 1,
    "title": "서울 맛집 추천",
    "content": "서울역 근처 맛집입니다."
  }
}

For list responses:

{
  "response": 200,
  "message": "게시글 목록 조회에 성공했습니다.",
  "data": {
    "items": [],
    "page": 1,
    "size": 10,
    "total": 0,
    "total_pages": 0
  }
}

For create responses:

{
  "response": 201,
  "message": "게시글 작성에 성공했습니다.",
  "data": {
    "id": 1
  }
}

For delete responses:

{
  "response": 200,
  "message": "게시글 삭제에 성공했습니다.",
  "data": null
}

The response field must match the actual HTTP status code.

Use Korean messages consistently.

Do not expose internal exception messages, stack traces, database errors, or OpenAI API errors through the message field.

## Error Response Format

Error responses must also use the common response structure.

Example:

{
  "response": 404,
  "message": "게시글을 찾을 수 없습니다.",
  "data": null
}

Password mismatch:

{
  "response": 403,
  "message": "비밀번호가 일치하지 않습니다.",
  "data": null
}

Validation failure:

{
  "response": 422,
  "message": "요청 데이터가 올바르지 않습니다.",
  "data": null
}

Internal server error:

{
  "response": 500,
  "message": "서버 내부 오류가 발생했습니다.",
  "data": null
}

Do not use different response shapes for different exceptions.

The following response formats are prohibited:

{
  "detail": "..."
}

{
  "error": "..."
}

{
  "message": "..."
}

All success and error responses must follow:

{
  "response": integer,
  "message": string,
  "data": any | null
}