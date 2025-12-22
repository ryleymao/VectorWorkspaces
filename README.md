# Multi-Tenant Knowledge Platform

> Multi-tenant, API-first knowledge platform with complete tenant isolation, versioned storage, and async processing. Features a RAG-powered query interface and modern React frontend.

## Why This Exists

Organizations need a way to:
- Query internal documentation and knowledge bases
- Keep data private (no external API calls)
- Support multiple teams/tenants securely with workspace collaboration
- Scale to handle high-volume queries
- Track document versions and freshness

This platform provides all of that, ready to deploy.

## Features

- **Multi-tenant Architecture** - Complete tenant isolation at database, vector storage, and API layers
- **Workspace Management** - Team collaboration with invite codes, member roles (Admin/Member), and RBAC
- **API-first Design** - RESTful API with service-layer architecture
- **Async Processing** - Celery + Redis for high-volume task orchestration
- **Versioned Storage** - Document versioning with freshness-aware retrieval
- **Database Engineering** - PostgreSQL with Alembic migrations and proper schema design
- **RAG Query Interface** - FAISS vector search + local Hugging Face LLM
- **Modern Frontend** - React + Tailwind CSS with routing and state management
- **Production Observability** - Prometheus metrics + structured logging
- **Cloud-Ready Deployment** - Dockerized with health checks and production configs

## Quick Start

### Docker (Recommended)

```bash
# Clone and start
git clone <repository-url>
cd Enterprise-AI-Knowledge-Agent
docker-compose up -d

# Run migrations
docker-compose exec api alembic upgrade head

# Access services
# API Docs: http://localhost:8000/docs
# Frontend: http://localhost:8080 (if running frontend)
```

### Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL & Redis
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload

# Start Celery worker (separate terminal)
celery -A celery_worker worker --loglevel=info
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:8080
```

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for detailed setup.

## Usage

### 1. Register & Login
```bash
POST /api/v1/auth/register  # Creates user + workspace (tenant)
POST /api/v1/auth/login     # Get JWT token
```

### 2. Workspace Management
```bash
GET  /api/v1/workspace/info              # Get workspace info
POST /api/v1/workspace/invite-code       # Generate invite code (Admin)
POST /api/v1/workspace/join              # Join workspace (creates account if needed)
GET  /api/v1/workspace/members           # List workspace members
PATCH /api/v1/workspace/members/{id}/role # Update member role (Admin)
DELETE /api/v1/workspace/members/{id}   # Remove member (Admin)
```

### 3. Ingest Knowledge
```bash
POST /api/v1/ingestion/upload    # Upload PDF/TXT/MD
POST /api/v1/ingestion/ingest    # API-based ingestion
```

### 4. Query Knowledge
```bash
POST /api/v1/chat/query  # RAG-powered answers
```

**API Docs**: http://localhost:8000/docs (when running)

## Tech Stack

**Backend:**
- FastAPI, PostgreSQL, FAISS, Redis, Celery
- Hugging Face (transformers, sentence-transformers)
- Alembic, SQLAlchemy, Pydantic

**Frontend:**
- React 18, React Router, Axios
- Tailwind CSS, Vite

**Infrastructure:**
- Docker, Docker Compose
- Prometheus, Grafana

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/v1/       # API endpoints (auth, workspace, ingestion, chat, etc.)
│   │   ├── core/         # Security, config, logging
│   │   ├── db/           # Database models & session
│   │   ├── services/     # Business logic
│   │   ├── tasks/        # Celery async tasks
│   │   └── schemas/      # Pydantic models
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/        # React pages (Login, Dashboard, Documents, Query, Workspace)
│   │   ├── components/   # Reusable components
│   │   └── contexts/     # React context (Auth)
│   └── package.json
├── monitoring/            # Prometheus & Grafana configs
├── storage/              # FAISS indices & uploaded documents
└── docker-compose.yml
```

## Configuration

Create `backend/.env` file and configure:

- `DATABASE_URL` - PostgreSQL connection string (default: `postgresql://postgres:postgres@localhost:5432/knowledge_agent`)
- `JWT_SECRET_KEY` - **Change this in production!** (default: `dev-secret-key-change-in-production`)
- `EMBEDDING_MODEL` - Hugging Face embedding model (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `LLM_MODEL` - Hugging Face LLM model (default: `facebook/opt-1.3b`)
- `REDIS_URL` - Redis connection string (default: `redis://localhost:6379/0`)
- `CELERY_BROKER_URL` - Celery broker URL (default: `redis://localhost:6379/0`)
- `CELERY_RESULT_BACKEND` - Celery result backend (default: `redis://localhost:6379/0`)

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for complete configuration details.

## Monitoring

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Deployment

**Local Development**: `docker-compose up -d`

**Production/Cloud**: This platform is **cloud-ready** and can be deployed to:
- AWS (ECS, EC2, EKS)
- Google Cloud (Cloud Run, GKE)
- Azure (Container Instances, AKS)
- Any Kubernetes cluster
- Or any server with Docker

## Documentation

- [Getting Started](docs/GETTING_STARTED.md) - Setup guide
- [Architecture](docs/ARCHITECTURE.md) - System design
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - How to work on this codebase
- [AI Agent Guide](docs/AI_AGENT_GUIDE.md) - Guide for AI agents

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file
