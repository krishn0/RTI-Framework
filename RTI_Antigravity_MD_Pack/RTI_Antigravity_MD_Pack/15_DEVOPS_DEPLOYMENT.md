# DevOps and Deployment

## MVP Deployment Topology
```text
Browser
 -> React/Vite frontend
 -> FastAPI backend
 -> PostgreSQL + pgvector
 -> local/S3-compatible document storage
 -> LLM/embedding provider
```

## Local Development
Keep current Docker Compose where possible.
Add pgvector-enabled PostgreSQL image/config if production-like local testing is needed.

## Required Environment Variables
```env
DATABASE_URL=
CORS_ORIGINS=
STORAGE_DIR=
LLM_PROVIDER=
LLM_API_KEY=
LLM_MODEL=
EMBEDDING_MODEL=
EMBEDDING_DIMENSION=
VECTOR_ENABLED=true
INTELLIGENCE_ENABLED=true
MAX_INVESTIGATION_AGENT_CALLS=10
MAX_UPLOAD_MB=20
```

## Health Checks
Add checks for:
- API
- DB
- vector extension
- storage write access
- optional LLM connectivity

## Background Work
MVP can use FastAPI/background tasks or current scheduler for controlled jobs.
For heavier production workloads, move intelligence tasks to a queue such as Celery + Redis.

## Logging
Every investigation should log:
- investigation ID
- step/agent
- duration
- status
- error type

Do not log full sensitive uploaded content unnecessarily.

## Deployment Gate
Before demo:
- fresh DB migration tested
- seed/sample case tested
- frontend API base URL verified
- upload path verified
- LLM key loaded securely
- end-to-end demo completed after deployment
