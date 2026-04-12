# CLAUDE.md — Python FastAPI Project

## Stack

Python 3.11+, FastAPI, PostgreSQL, SQLAlchemy (async), Alembic migrations,
JWT auth, Redis, deployed on Cloudflare Workers via Pyodide or as a
containerized service.

## Folder structure

```
src/
├── main.py           ← FastAPI app instance, middleware, router mounts
├── routers/          ← one file per resource (auth.py, game.py, etc.)
├── models/           ← SQLAlchemy ORM models
├── schemas/          ← Pydantic request/response schemas
├── services/         ← business logic — the only layer that touches the DB
├── core/
│   ├── config.py     ← settings via pydantic-settings, reads from env
│   ├── database.py   ← async SQLAlchemy engine and session
│   ├── security.py   ← JWT creation, hashing, token validation
│   └── redis.py      ← Redis client instance
├── middleware/        ← rate limiting, CORS, auth middleware
└── tests/            ← pytest test files mirroring src structure
```

## Naming conventions

- Files and folders: snake_case (game_state.py)
- Classes: PascalCase (GameState, UserService)
- Functions and variables: snake_case (get_current_user)
- Database tables: snake_case plural (game_states, attack_logs)
- Env vars: UPPER_SNAKE_CASE (DATABASE_URL, JWT_SECRET)
- Routes: kebab-case URLs (/api/v1/game-state)

## Route conventions

- All routes prefixed with /api/v1
- One router file per resource in src/routers/
- Routers mounted in main.py
- Pydantic schemas validate all input and output — never raw dicts

## Middleware order

```
CORS → rate-limit → auth → validation (Pydantic) → handler → error-handler
```

## Error handling

- Raise HTTPException with status_code and detail
- Global exception handler in main.py catches unhandled errors
- Never expose stack traces or internal details in responses
- Format: {"error": {"code": "NOT_FOUND", "message": "Game not found"}}

## Auth

- JWT access tokens, short-lived (15 min)
- Refresh tokens stored in Redis, rotated on use
- get_current_user dependency injected into protected routes
- Password hashing: bcrypt via passlib
- Never trust client-side claims — always validate server-side

## Data access

- All DB access through SQLAlchemy async sessions in src/services/
- Routers never import SQLAlchemy directly — call service functions only
- Single async engine in src/core/database.py
- Redis for caching, rate limiting, WebSocket state via src/core/redis.py
- Alembic for all migrations — never modify schema manually

## WebSocket

- Mount WebSocket endpoints in main.py
- Use Redis pub/sub for broadcasting state to multiple clients
- Always handle disconnect gracefully — clean up Redis keys on close

## Real-time simulation (game tick pattern)

```python
# Background task pattern for game simulation
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(game_tick_loop())
    yield

async def game_tick_loop():
    while True:
        await simulate_tick()
        await broadcast_state()
        await asyncio.sleep(1/20)  # 20 ticks per second
```

## Testing

- Framework: pytest + pytest-asyncio + httpx (async test client)
- Test files: tests/test_[resource].py
- Run: pytest (all) / pytest tests/test_game.py (subset)
- Minimum: test all routes, auth flows, game tick logic, attack wave generation

## Commands

```bash
uvicorn src.main:app --reload     # dev server (port 8000)
alembic upgrade head              # run migrations
alembic revision --autogenerate -m "description"  # create migration
pytest                            # run tests
pytest --cov=src                  # run tests with coverage
```

## Environment variables required

```
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/dbname
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-here
JWT_ALGORITHM=HS256
ALLOWED_ORIGINS=http://localhost:3000
```
