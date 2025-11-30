# Learning Assistant (DS Club 2025)

A full-stack learning assistant for generating materials, homework, grading submissions with an AI grader, chat, and mind maps.

## Prerequisites
- Docker and Docker Compose v2
- Python 3.11 (for local dev, optional if using Docker)
- Node.js 18+ and pnpm or npm (for frontend)
- OpenAI API key

## Environment Variables
Create a `.env` file at repo root (used by docker-compose):
```
OPENAI_API_KEY=sk-...
SECRET_KEY=change_this_in_prod
```
Backend reads `DATABASE_URL` from docker-compose (Postgres in container).

## Run with Docker (recommended)
1. Build and start services:
   ```bash
   docker compose up --build
   ```
   - The API will wait for Postgres health and run Alembic migrations automatically, then start on http://localhost:8000
2. Stop:
   ```bash
   docker compose down
   ```

## Local development (backend)
1. Create and activate venv, then install deps:
   ```bash
   python -m venv .venv
   . .venv/bin/activate  # Windows: .venv\\Scripts\\activate
   pip install -r requirements.txt
   ```
2. Start Postgres (locally or via Docker). Example using Docker:
   ```bash
   docker run --name la-db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=learning_assistant -p 5432:5432 -v pgdata:/var/lib/postgresql/data -d postgres:16
   ```
3. Set env vars and run migrations:
   ```bash
   export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/learning_assistant
   export OPENAI_API_KEY=sk-...
   export SECRET_KEY=dev-secret
   alembic upgrade head
   ```
4. Run API:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## Frontend
1. Install deps and run dev server:
   ```bash
   cd frontend
   npm install   # or pnpm i
   npm run dev
   ```
2. The app expects backend at `http://localhost:8000` (configured in `frontend/src/api.ts`).

## Application Flow
- Sessions
  - Create/select a session from the sidebar. On creation, you’re prompted for a name.
- Materials
  - Upload files to a session. They populate the vector store for context.
- Homework
  - Generate homework via the modal (topic, difficulty, select materials).
  - Open a homework to view tasks; upload a file per task.
  - PDFs are parsed to text (server-side) and uploaded to the vector store; originals fallback if parsing fails.
  - Submit homework when ready; the AI grader reviews all tasks and produces feedback and scores.
- Mind Maps
  - Generate and list mind maps for the current session.
- Chat
  - Chat is scoped to the current session for context.

## Migrations
- Auto-run in Docker on container start: `alembic upgrade head`.
- Manual:
  ```bash
  alembic revision -m "desc"
  alembic upgrade head
  ```

## Common Issues
- 404 on upload
  - Ensure `task_id` belongs to `homework_id` (GET `/api/homework/{id}`), backend now verifies and returns clear error.
- PDF not graded
  - Ensure OpenAI API key is set. PDFs are parsed with `pypdf`; if parsing fails, raw bytes are uploaded.
- CORS
  - CORS is permissive in dev; adjust in `app/main.py` for prod.

## Tech Stack
- Backend: FastAPI, SQLAlchemy, Alembic, asyncpg
- AI: OpenAI Assistants API with vector stores
- Frontend: React + Tailwind + Vite (in `frontend`)
- DB: Postgres 16

## Scripts and Commands
- Docker:
  - `docker compose up --build` — build and run
  - `docker compose down` — stop
- Backend (local):
  - `alembic upgrade head` — run migrations
  - `uvicorn app.main:app --reload` — dev server
- Frontend:
  - `npm run dev` — dev
  - `npm run build && npm run preview` — build/preview

## Security Notes
- Do not commit real API keys. Use dotenv or CI secrets.
- Set a strong `SECRET_KEY` in production.

## License
MIT