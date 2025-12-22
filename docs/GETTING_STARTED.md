# Getting Started

## Quick Start (Docker)

```bash
# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# Access services
# API Docs: http://localhost:8000/docs
# Health Check: http://localhost:8000/health
# Metrics: http://localhost:8000/metrics
```

**Note**: The API container may take 30-60 seconds to start while AI models load.

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL & Redis
docker-compose up -d postgres redis

# Wait for services to be healthy (about 10 seconds)

# Run database migrations
alembic upgrade head

# Start API server
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: http://localhost:8080

### Celery Worker (Optional, for async processing)

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Start Celery worker
celery -A celery_worker worker --loglevel=info
```

## First Steps

### 1. Register a User

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword",
    "tenant_name": "My Workspace"
  }'
```

**Via Frontend:**
1. Navigate to http://localhost:8080
2. Click "Register"
3. Fill in email, name, password, and workspace name
4. Submit form

### 2. Login

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

Save the `access_token` from the response.

**Via Frontend:**
1. Navigate to http://localhost:8080/login
2. Enter email and password
3. Submit form (you'll be redirected to dashboard)

### 3. Upload a Document

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/ingestion/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/document.pdf"
```

**Via Frontend:**
1. Navigate to "Documents" page
2. Click "Choose File" and select a PDF, TXT, or MD file
3. Click "Upload Document"

### 4. Query Knowledge Base

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?",
    "top_k": 5
  }'
```

**Via Frontend:**
1. Navigate to "Query" page
2. Enter your question
3. Click "Query"

### 5. Manage Workspace

**Generate Invite Code (Admin only):**
```bash
curl -X POST http://localhost:8000/api/v1/workspace/invite-code \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Join Workspace (creates account if needed):**
```bash
curl -X POST http://localhost:8000/api/v1/workspace/join \
  -H "Content-Type: application/json" \
  -d '{
    "invite_code": "generated-invite-code",
    "email": "newuser@example.com",
    "name": "New User",
    "password": "securepassword"
  }'
```

**View Workspace Members:**
```bash
curl -X GET http://localhost:8000/api/v1/workspace/members \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Configuration

### Environment Variables

Create `backend/.env` file:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/knowledge_agent

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# AI Models
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LLM_MODEL=facebook/opt-1.3b

# Chunking
CHUNK_SIZE=500
CHUNK_OVERLAP=250

# Storage
FAISS_STORAGE_PATH=./storage/faiss_indices

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Frontend Configuration

The frontend connects to `http://localhost:8000` by default. To change this, edit `frontend/vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // Change this
      changeOrigin: true
    }
  }
}
```

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running: `docker ps`
- Check connection string in `.env`
- Verify database exists: `docker-compose exec postgres psql -U postgres -l`

### Migration Errors
- Ensure database is running
- Check Alembic version: `alembic current`
- Try: `alembic upgrade head --sql` to see SQL without executing

### API Not Starting
- Check logs: `docker-compose logs api`
- Verify all dependencies installed: `pip list`
- Check port 8000 is not in use

### Frontend Not Connecting
- Verify API is running at http://localhost:8000
- Check browser console for errors
- Verify CORS settings (should work with proxy)

### Celery Worker Not Processing Tasks
- Ensure Redis is running
- Check worker logs: `celery -A celery_worker worker --loglevel=debug`
- Verify Redis connection string

## Next Steps

- Explore API documentation at http://localhost:8000/docs
- Read [Architecture](./ARCHITECTURE.md) for system design details
- Check monitoring setup in `docker-compose.monitoring.yml`
- Review code structure in `backend/app/` and `frontend/src/`
