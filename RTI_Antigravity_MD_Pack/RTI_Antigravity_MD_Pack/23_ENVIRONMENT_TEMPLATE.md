# Environment Configuration Template

Create a real `.env` from this list. Do not commit secrets.

```env
# Core
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DB
STORAGE_DIR=./storage
CORS_ORIGINS=http://localhost:5173

# Existing CoreScapper behavior
BOOTSTRAP_LIVE_SOURCES=true
RECOVER_ORPHANED_RUNS=true

# Intelligence Layer
INTELLIGENCE_ENABLED=true
VECTOR_ENABLED=true

# LLM
LLM_PROVIDER=
LLM_API_KEY=
LLM_MODEL=
LLM_TIMEOUT_SECONDS=60
MAX_INVESTIGATION_AGENT_CALLS=10

# Embeddings
EMBEDDING_MODEL=
EMBEDDING_DIMENSION=
EMBEDDING_BATCH_SIZE=32

# Retrieval
RAG_TOP_K_VECTOR=12
RAG_TOP_K_KEYWORD=12
RAG_FINAL_K=8

# Uploads
MAX_UPLOAD_MB=20
ALLOWED_UPLOAD_TYPES=application/pdf,text/plain

# Optional future queue
REDIS_URL=
```

## Validation Rule
Application startup must validate required variables for enabled features and fail with a clear message rather than failing later during an investigation.
