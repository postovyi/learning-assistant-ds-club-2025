# Learning Assistant (DS Club 2025)

A full-stack learning assistant for generating materials, homework, grading submissions with an AI grader, chat, and mind maps.

## Prerequisites
- Docker and Docker Compose v2
- Python 3.11 (for local dev, optional if using Docker)
- Node.js 18+ and npm (for frontend)
- OpenAI API key

## Environment Variables
Create a `.env` file at repo root (used by docker-compose):
```
OPENAI_API_KEY=sk-...
SECRET_KEY=change_this_in_prod
```
Backend reads `DATABASE_URL` from docker-compose (Postgres in container).

## Quick Start (Recommended)

### 1. Start Backend with Docker
```bash
docker compose up --build
```
- The API will wait for Postgres health and run Alembic migrations automatically
- Backend will be available at http://localhost:8000

### 2. Start Frontend (in a separate terminal)
```bash
cd frontend
npm install
npm run dev
```
- Frontend will be available at http://localhost:5173 (or the port shown in terminal)
- The app will automatically connect to the backend at http://localhost:8000

### 3. Access the Application
Open your browser and navigate to http://localhost:5173

### 4. Stop Services
- Frontend: Press `Ctrl+C` in the frontend terminal
- Backend: 
  ```bash
  docker compose down
  ```

## Local Development (Backend)
If you prefer to run the backend without Docker:

1. Create and activate venv, then install deps:
   ```bash
   python -m venv .venv
   . .venv/bin/activate  # Windows: .venv\Scripts\activate
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

The frontend is a Single Page Application (SPA) built with React, TypeScript, Tailwind CSS, and Vite.

### Structure
- **Layout**: Sidebar navigation with main content area
- **Contexts**: `AuthContext` for user management, `SessionContext` for workspace isolation
- **Components**: Modular components for Materials, Homework, Chat, and Mind Maps

### Features
- **Authentication**: Login and Register pages with JWT handling
- **Session Management**: Create and switch between study sessions
- **Material Management**: Upload and view study materials (PDFs, text)
- **Homework Interface**: 
  - Generate homework assignments based on selected materials
  - View detailed tasks and upload solutions
  - Submit homework for AI grading and view feedback
- **Interactive Chat**: Context-aware chat with the AI assistant
- **Mind Maps**: Visual representation of generated concepts

### Setup
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start development server:
   ```bash
   npm run dev
   ```
3. The app expects backend at `http://localhost:8000` (configured in `frontend/src/api.ts`)

### Build for Production
```bash
cd frontend
npm run build
npm run preview  # Preview production build
```

## Application Flow
- **Sessions**
  - Create/select a session from the sidebar. On creation, you're prompted for a name.
- **Materials**
  - Upload files to a session. They populate the vector store for context.
- **Homework**
  - Generate homework via the modal (topic, difficulty, select materials).
  - Open a homework to view tasks; upload a file per task.
  - PDFs are parsed to text (server-side) and uploaded to the vector store; originals fallback if parsing fails.
  - Submit homework when ready; the AI grader reviews all tasks and produces feedback and scores.
- **Mind Maps**
  - Generate and list mind maps for the current session.
- **Chat**
  - Chat is scoped to the current session for context.

## Migrations
- Auto-run in Docker on container start: `alembic upgrade head`.
- Manual:
  ```bash
  alembic revision -m "desc"
  alembic upgrade head
  ```

## Common Issues
- **404 on upload**
  - Ensure `task_id` belongs to `homework_id` (GET `/api/homework/{id}`), backend now verifies and returns clear error.
- **PDF not graded**
  - Ensure OpenAI API key is set. PDFs are parsed with `pypdf`; if parsing fails, raw bytes are uploaded.
- **CORS**
  - CORS is permissive in dev; adjust in `app/main.py` for prod.
- **Frontend can't connect to backend**
  - Ensure backend is running on http://localhost:8000
  - Check `frontend/src/api.ts` for the correct baseURL

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Alembic, asyncpg
- **AI**: OpenAI Assistants API with vector stores
- **Frontend**: React, TypeScript, Tailwind CSS, Vite
- **DB**: Postgres 16

## Scripts and Commands
- **Docker**:
  - `docker compose up --build` — build and run backend
  - `docker compose down` — stop backend
- **Backend (local)**:
  - `alembic upgrade head` — run migrations
  - `uvicorn app.main:app --reload` — dev server
- **Frontend**:
  - `npm install` — install dependencies
  - `npm run dev` — start dev server
  - `npm run build && npm run preview` — build and preview production

## Security Notes
- Do not commit real API keys. Use dotenv or CI secrets.
- Set a strong `SECRET_KEY` in production.

## License
MIT