# Developer Guide

This guide helps developers and AI agents understand how to work on this codebase effectively.

## Table of Contents

- [Codebase Overview](#codebase-overview)
- [Architecture Patterns](#architecture-patterns)
- [Development Workflow](#development-workflow)
- [Adding New Features](#adding-new-features)
- [Code Style & Conventions](#code-style--conventions)
- [Testing](#testing)
- [Common Tasks](#common-tasks)
- [For AI Agents](#for-ai-agents)

## Codebase Overview

### Project Structure

```
.
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints (REST routes)
│   │   ├── core/           # Core functionality (config, security, logging)
│   │   ├── db/             # Database models and session management
│   │   ├── services/       # Business logic layer
│   │   ├── tasks/          # Celery async tasks
│   │   └── schemas/        # Pydantic models for validation
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container definition
├── frontend/                # React frontend
│   ├── src/
│   │   ├── pages/          # Page components
│   │   ├── components/     # Reusable components
│   │   └── contexts/      # React context providers
│   └── package.json        # Node dependencies
├── monitoring/             # Prometheus & Grafana configs
├── storage/                # FAISS indices and uploaded files
└── docker-compose.yml      # Local development orchestration
```

### Key Technologies

**Backend:**
- FastAPI - Web framework
- SQLAlchemy - ORM
- Alembic - Migrations
- Pydantic - Data validation
- Celery - Async tasks
- FAISS - Vector search

**Frontend:**
- React 18 - UI framework
- React Router - Routing
- Tailwind CSS - Styling
- Axios - HTTP client
- Vite - Build tool

## Architecture Patterns

### Service Layer Pattern

**Rule**: API endpoints should be thin wrappers that delegate to service functions.

```python
# Good: API endpoint delegates to service
@router.post("/upload")
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    return ingestion_service.upload_document(db, file)

# Bad: Business logic in API endpoint
@router.post("/upload")
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    # Don't put business logic here
    content = await file.read()
    # ... processing logic ...
```

**Why**: Separates concerns, makes code testable, allows reuse.

### Dependency Injection

**Rule**: Use FastAPI `Depends()` for database sessions, authentication, and tenant extraction.

```python
# Standard pattern for protected endpoints
@router.get("/items")
async def get_items(
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    # tenant_id and db are automatically injected
    return service.get_items(db, tenant_id)
```

**Common Dependencies:**
- `get_db` - Database session
- `get_current_user` - Authenticated user
- `get_current_tenant` - Tenant ID from JWT
- `require_admin_role` - Admin-only access

### Multi-Tenancy Enforcement

**Rule**: Always filter by `tenant_id` in database queries.

```python
# Good: Tenant-scoped query
def get_documents(db: Session, tenant_id: int):
    return db.query(Document).filter(Document.tenant_id == tenant_id).all()

# Bad: Missing tenant filter
def get_documents(db: Session):
    return db.query(Document).all()  # Security risk!
```

**Why**: Ensures complete data isolation between tenants.

## Development Workflow

### 1. Setup Environment

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install

# Start infrastructure
docker-compose up -d postgres redis
```

### 2. Run Migrations

```bash
cd backend
alembic upgrade head
```

### 3. Start Development Servers

```bash
# Terminal 1: Backend API
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Celery Worker (optional)
cd backend
celery -A celery_worker worker --loglevel=info
```

### 4. Make Changes

- Backend changes auto-reload (--reload flag)
- Frontend changes hot-reload (Vite HMR)
- Database changes require new migration

### 5. Create Migration

```bash
cd backend
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

## Adding New Features

### Adding a New API Endpoint

**Step 1**: Create Pydantic schema in `app/schemas/`

```python
# app/schemas/example.py
from pydantic import BaseModel

class ExampleCreate(BaseModel):
    name: str
    description: str

class ExampleResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True
```

**Step 2**: Create service function in `app/services/`

```python
# app/services/example_service.py
from sqlalchemy.orm import Session
from app.db.models.example import Example
from app.schemas.example import ExampleCreate

def create_example(db: Session, tenant_id: int, data: ExampleCreate):
    example = Example(
        tenant_id=tenant_id,
        name=data.name,
        description=data.description
    )
    db.add(example)
    db.commit()
    db.refresh(example)
    return example
```

**Step 3**: Create API endpoint in `app/api/v1/`

```python
# app/api/v1/example.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_tenant
from app.schemas.example import ExampleCreate, ExampleResponse
from app.services import example_service

router = APIRouter()

@router.post("/", response_model=ExampleResponse)
async def create_example(
    data: ExampleCreate,
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    return example_service.create_example(db, tenant_id, data)
```

**Step 4**: Register router in `app/main.py`

```python
from app.api.v1 import example

app.include_router(example.router, prefix="/api/v1/example", tags=["example"])
```

### Adding a New Frontend Page

**Step 1**: Create page component in `frontend/src/pages/`

```javascript
// frontend/src/pages/Example.jsx
import { useState } from 'react'
import axios from 'axios'

export default function Example() {
  const [data, setData] = useState(null)
  
  const handleSubmit = async () => {
    const response = await axios.post('/api/v1/example', {
      name: 'Test',
      description: 'Test description'
    })
    setData(response.data)
  }
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Example Page</h1>
      <button onClick={handleSubmit}>Submit</button>
    </div>
  )
}
```

**Step 2**: Add route in `frontend/src/App.jsx`

```javascript
import Example from './pages/Example'

<Route path="example" element={<Example />} />
```

**Step 3**: Add navigation link in `frontend/src/components/Layout.jsx`

```javascript
{ path: '/example', label: 'Example' }
```

### Adding a New Database Model

**Step 1**: Create model in `app/db/models/`

```python
# app/db/models/example.py
from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class Example(Base):
    __tablename__ = "examples"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
```

**Step 2**: Import in `app/db/models/__init__.py`

```python
from .example import Example
```

**Step 3**: Create migration

```bash
alembic revision --autogenerate -m "add example table"
alembic upgrade head
```

**Important**: Always include `tenant_id` for multi-tenancy!

## Code Style & Conventions

### Python

- **Type Hints**: Use type hints for function parameters and returns
- **Docstrings**: Add docstrings for public functions (if needed)
- **Naming**: 
  - Functions: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Imports**: Group imports (stdlib, third-party, local)

```python
# Good
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import User

def get_users(db: Session, tenant_id: int) -> List[User]:
    """Get all users for a tenant."""
    return db.query(User).filter(User.tenant_id == tenant_id).all()
```

### JavaScript/React

- **Components**: PascalCase for component names
- **Functions**: camelCase for functions
- **Hooks**: Prefix with `use` (e.g., `useAuth`)
- **Props**: Destructure props in function signature

```javascript
// Good
export default function UserProfile({ userId, name }) {
  const { user, loading } = useAuth()
  
  if (loading) return <div>Loading...</div>
  
  return <div>{name}</div>
}
```

### File Naming

- **Python**: `snake_case.py`
- **React Components**: `PascalCase.jsx`
- **Utilities**: `snake_case.js` or `camelCase.js`

## Testing

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests (if configured)
cd frontend
npm test
```

### Writing Tests

**Backend Test Example:**

```python
# tests/test_example.py
import pytest
from app.services import example_service
from app.db.session import SessionLocal

def test_create_example():
    db = SessionLocal()
    try:
        result = example_service.create_example(
            db, 
            tenant_id=1, 
            data=ExampleCreate(name="Test", description="Test")
        )
        assert result.name == "Test"
    finally:
        db.close()
```

## Common Tasks

### Adding a New Field to Existing Model

1. Add column to model in `app/db/models/`
2. Create migration: `alembic revision --autogenerate -m "add field"`
3. Update Pydantic schema in `app/schemas/`
4. Update service functions if needed
5. Run migration: `alembic upgrade head`

### Adding Authentication to New Endpoint

```python
from app.core.dependencies import get_current_user, get_current_tenant

@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    # Endpoint is now protected
    return {"user_id": current_user.id, "tenant_id": tenant_id}
```

### Adding Admin-Only Endpoint

```python
from app.core.dependencies import require_admin_role

@router.delete("/admin-only", dependencies=[Depends(require_admin_role)])
async def admin_endpoint():
    # Only admins can access
    return {"message": "Admin access"}
```

### Adding Async Task

1. Create task function in `app/tasks/`

```python
# app/tasks/example_tasks.py
from app.tasks.celery_app import celery_app

@celery_app.task
def process_example(example_id: int):
    # Async processing
    pass
```

2. Call from service or API endpoint

```python
from app.tasks.example_tasks import process_example

process_example.delay(example_id)
```

## For AI Agents

### How to Approach This Codebase

1. **Understand the Architecture First**
   - Read `docs/ARCHITECTURE.md` for system design
   - Understand service layer pattern
   - Know multi-tenancy enforcement

2. **Follow Existing Patterns**
   - Look at similar features for reference
   - Match code style and structure
   - Use existing dependencies and utilities

3. **Respect Multi-Tenancy**
   - Always include `tenant_id` in queries
   - Use `get_current_tenant` dependency
   - Never expose cross-tenant data

4. **Service Layer First**
   - Implement business logic in services
   - Keep API endpoints thin
   - Make services testable

5. **Update Documentation**
   - Update relevant docs when adding features
   - Add examples to this guide if creating new patterns
   - Keep README.md current

### Common Patterns to Recognize

**Authentication Pattern:**
```python
current_user: User = Depends(get_current_user)
tenant_id: int = Depends(get_current_tenant)
```

**Service Call Pattern:**
```python
result = service_function(db, tenant_id, data)
```

**Error Handling Pattern:**
```python
try:
    result = service_function(...)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

**Database Query Pattern:**
```python
db.query(Model).filter(Model.tenant_id == tenant_id).filter(...).all()
```

### When Making Changes

1. **Check Dependencies**: Ensure tenant_id is included
2. **Check Permissions**: Verify RBAC if needed
3. **Check Migrations**: Create migration for schema changes
4. **Check Tests**: Add/update tests for new features
5. **Check Docs**: Update relevant documentation

### Code Search Strategy

- Use semantic search for understanding features
- Use grep for finding specific patterns
- Check `app/main.py` for router registration
- Check `app/db/models/__init__.py` for model imports
- Check `alembic/versions/` for migration history

## Troubleshooting

### Database Connection Issues
- Check `DATABASE_URL` in `.env`
- Verify PostgreSQL is running: `docker ps`
- Check migration status: `alembic current`

### Import Errors
- Ensure virtual environment is activated
- Check `__init__.py` files exist
- Verify Python path includes `backend/`

### Frontend Build Issues
- Clear `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (should be 18+)
- Clear Vite cache: `rm -rf node_modules/.vite`

### Migration Conflicts
- Check current migration: `alembic current`
- Review migration files in `alembic/versions/`
- Consider manual migration if auto-generate fails

## Getting Help

- Check existing code for similar patterns
- Review `docs/ARCHITECTURE.md` for design decisions
- Check API docs at `/docs` endpoint
- Review git history for context on changes

