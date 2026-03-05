# Beraxis – Global SaaS AI Calling Agent Platform

The complete production-ready backend for Beraxis. Designed for multi-tenant SaaS architectures combining AI (STT/LLM/TTS) with telephony (Asterisk ARI).

## Tech Stack
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL + SQLAlchemy + Alembic
- **Queues**: Redis + Celery
- **AI Stack**: Faster-Whisper, Llama 3 (llama.cpp), Piper TTS
- **Telephony**: Asterisk ARI
- **Containerization**: Docker Compose

## Quickstart (Development)

1. **Environment Config**
   Copy `.env.example` to `.env` and fill in necessary details (DB passwords, Stripe keys, etc.).
   ```bash
   cp .env.example .env
   ```

2. **Start Infrastructure (DB & Redis)**
   ```bash
   docker-compose up -d postgres redis
   ```

3. **Install Dependencies Locally**
   We recommend using a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```bash
   # Make sure DB is up first
   alembic upgrade head
   ```
   *(Note: Since models were just created, you'll need to run `alembic revision --autogenerate -m "init"` first)*

5. **Start API Server**
   ```bash
   uvicorn app.main:app --reload
   ```
   Visit `http://localhost:8000/docs` to see the automatically generated OpenAPI specs.

## Production Deployment (VPS)

For a production deployment, especially with AI models running locally, a dedicated GPU server is recommended (e.g., Ubuntu 22.04 with an RTX 3090/4090).

1. Install `docker` and `docker-compose`.
2. Configure your `nginx.conf` and build the frontend to `../dist`.
3. Start the entire stack:
   ```bash
   docker-compose up -d --build
   ```

**Important**:
- You must provide your own SIP trunk details to Asterisk for outbound calling to work.
- The `Dockerfile.ai` will compile `llama.cpp` for CUDA. Ensure Nvidia Container Toolkit is installed on the host.

## Project Structure
- `app/api/`: Routers grouped by feature (auth, dashboard, campaigns, calls, agents, billing, admin).
- `app/models/`: SQLAlchemy ORM definitions.
- `app/services/`: Core logic (JWT auth, campaign orchestration).
- `app/ai/`: Speech-to-Text, LLM Logic, and Text-to-Speech wrappers.
- `app/telephony/`: Asterisk channel bridges.
- `app/workers/`: Background task queues (Celery).
