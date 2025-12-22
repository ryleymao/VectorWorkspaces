# AI Agent Guide

This guide helps AI agents understand how to effectively work with this codebase.

## Quick Reference

### Codebase Type
- **Backend**: Python FastAPI (async web framework)
- **Frontend**: React 18 with TypeScript-like patterns
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Architecture**: Multi-tenant SaaS platform

### Critical Rules

1. **Always enforce multi-tenancy** - Every database query must filter by `tenant_id`
2. **Use service layer pattern** - Business logic goes in `services/`, not in API endpoints
3. **Follow dependency injection** - Use FastAPI `Depends()` for auth, DB, tenant
4. **Respect RBAC** - Use `require_admin_role` for admin-only endpoints
5. **Create migrations** - Schema changes require Alembic migrations

## Understanding the Codebase

### Key Directories

```
backend/app/
├── api/v1/          # API endpoints - thin wrappers around services
├── services/        # Business logic - where most code lives
├── db/models/       # Database models - SQLAlchemy ORM
├── schemas/         # Pydantic models - request/response validation
├── core/            # Core utilities - config, security, logging
└── tasks/           # Celery async tasks

frontend/src/
├── pages/           # Page components
├── components/      # Reusable components
└── contexts/        # React context (auth state)
```

### Request Flow

```
HTTP Request
  ↓
FastAPI Router (api/v1/)
  ↓
Dependency Injection (auth, tenant_id, db)
  ↓
Service Layer (services/)
  ↓
Database/FAISS/Redis
  ↓
Response
```

## Common Tasks for AI Agents

### Task: Add a New API Endpoint

**Steps:**
1. Check if similar endpoint exists (search `api/v1/`)
2. Create Pydantic schema in `schemas/` (request + response)
3. Create service function in `services/` (business logic)
4. Create API endpoint in `api/v1/` (thin wrapper)
5. Register router in `main.py`
6. Ensure tenant_id is included in service call

**Example Pattern:**
```python
# 1. Schema (schemas/example.py)
class ExampleCreate(BaseModel):
    name: str

# 2. Service (services/example_service.py)
def create_example(db: Session, tenant_id: int, data: ExampleCreate):
    obj = Example(tenant_id=tenant_id, name=data.name)
    db.add(obj)
    db.commit()
    return obj

# 3. API (api/v1/example.py)
@router.post("/", response_model=ExampleResponse)
async def create_example(
    data: ExampleCreate,
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    return example_service.create_example(db, tenant_id, data)
```

### Task: Add a New Database Model

**Steps:**
1. Create model in `db/models/` with `tenant_id` column
2. Import in `db/models/__init__.py`
3. Create Alembic migration: `alembic revision --autogenerate`
4. Review migration file for correctness
5. Apply migration: `alembic upgrade head`

**Critical**: Always include `tenant_id` for multi-tenancy!

```python
class Example(Base):
    __tablename__ = "examples"
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)  # REQUIRED
    # ... other fields
```

### Task: Add Authentication to Endpoint

**Pattern:**
```python
from app.core.dependencies import get_current_user, get_current_tenant

@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant)
):
    # Now has access to user and tenant_id
    pass
```

### Task: Add Admin-Only Endpoint

**Pattern:**
```python
from app.core.dependencies import require_admin_role

@router.delete("/admin", dependencies=[Depends(require_admin_role)])
async def admin_endpoint():
    # Only admins can access
    pass
```

### Task: Add Frontend Page

**Steps:**
1. Create page component in `frontend/src/pages/`
2. Add route in `frontend/src/App.jsx`
3. Add navigation link in `frontend/src/components/Layout.jsx`
4. Use `useAuth()` hook for authentication
5. Use `axios` for API calls

**Pattern:**
```javascript
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'

export default function NewPage() {
  const { token } = useAuth()
  
  const fetchData = async () => {
    const response = await axios.get('/api/v1/endpoint')
    // Handle response
  }
  
  return <div>...</div>
}
```

## Code Patterns to Recognize

### Multi-Tenancy Pattern
```python
# Good: Always filter by tenant_id
def get_items(db: Session, tenant_id: int):
    return db.query(Item).filter(Item.tenant_id == tenant_id).all()

# Bad: Never query without tenant filter
def get_items(db: Session):
    return db.query(Item).all()  # SECURITY RISK
```

### Service Layer Pattern
```python
# Good: Business logic in service
def create_item(db: Session, tenant_id: int, data: ItemCreate):
    item = Item(tenant_id=tenant_id, **data.dict())
    db.add(item)
    db.commit()
    return item

# Bad: Don't put logic in API endpoint
@router.post("/")
async def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    # Don't put business logic here
    pass
```

### Error Handling Pattern
```python
from fastapi import HTTPException

try:
    result = service_function(...)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

### Database Query Pattern
```python
# Standard query with tenant filter
items = db.query(Item)\
    .filter(Item.tenant_id == tenant_id)\
    .filter(Item.status == "active")\
    .order_by(Item.created_at.desc())\
    .all()

# Count query
count = db.query(Item)\
    .filter(Item.tenant_id == tenant_id)\
    .count()
```

## Search Strategies

### Finding Similar Code

**For API endpoints:**
```
Search: "How are [similar feature] endpoints implemented?"
Look in: app/api/v1/
```

**For services:**
```
Search: "How does [similar feature] service work?"
Look in: app/services/
```

**For models:**
```
Search: "What database models exist for [domain]?"
Look in: app/db/models/
```

### Understanding Dependencies

**Check imports:**
- `app/main.py` - See all registered routers
- `app/db/models/__init__.py` - See all models
- `app/core/dependencies.py` - See available dependencies

**Check usage:**
- Use grep to find where functions are called
- Check service functions for business logic patterns
- Review migrations for schema evolution

## Common Mistakes to Avoid

### Bad: Missing Tenant Filter
```python
# WRONG - Security vulnerability
def get_documents(db: Session):
    return db.query(Document).all()
```

### Bad: Business Logic in API Layer
```python
# WRONG - Should be in service
@router.post("/")
async def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    item = Item(**data.dict())  # Business logic here
    db.add(item)
    db.commit()
```

### Bad: Missing Migration
```python
# WRONG - Changed model but no migration
class Item(Base):
    new_field = Column(String)  # Added field but no migration
```

### Bad: Cross-Tenant Data Access
```python
# WRONG - Not filtering by tenant
def get_user(user_id: int, db: Session):
    return db.query(User).filter(User.id == user_id).first()
    # Missing tenant_id check!
```

## When Making Changes

### Checklist

- [ ] Does it respect multi-tenancy? (tenant_id filter)
- [ ] Is business logic in service layer?
- [ ] Are dependencies injected correctly?
- [ ] Is RBAC enforced if needed?
- [ ] Is migration created for schema changes?
- [ ] Are error cases handled?
- [ ] Is logging added for important operations?
- [ ] Is documentation updated?

### Testing Your Changes

1. **Start services**: `docker-compose up -d postgres redis`
2. **Run migrations**: `alembic upgrade head`
3. **Start API**: `uvicorn app.main:app --reload`
4. **Test endpoint**: Use `/docs` Swagger UI or curl
5. **Check logs**: Look for errors in console
6. **Verify tenant isolation**: Test with different tenants

## Understanding Existing Code

### Reading a Feature

1. **Start with API endpoint** (`api/v1/`) - See what it exposes
2. **Check service function** (`services/`) - Understand business logic
3. **Review database model** (`db/models/`) - See data structure
4. **Check schemas** (`schemas/`) - Understand request/response format
5. **Look for tests** (`tests/`) - See expected behavior

### Tracing a Request

1. Find API endpoint in `api/v1/`
2. Follow dependencies (auth, tenant, db)
3. Find service function call
4. Check database queries
5. Review response construction

## Code Generation Guidelines

### When Generating Code

1. **Match existing patterns** - Look for similar code first
2. **Include tenant_id** - Always for multi-tenancy
3. **Use type hints** - Python type annotations
4. **Add error handling** - Try/except with appropriate HTTP exceptions
5. **Follow naming conventions** - snake_case for Python, camelCase for JS
6. **Add logging** - Use structured logging for important operations

### Code Template for New Endpoint

```python
# schemas/example.py
from pydantic import BaseModel

class ExampleCreate(BaseModel):
    name: str

class ExampleResponse(BaseModel):
    id: int
    tenant_id: int
    name: str
    
    class Config:
        from_attributes = True

# services/example_service.py
from sqlalchemy.orm import Session
from app.db.models.example import Example
from app.schemas.example import ExampleCreate, ExampleResponse

def create_example(db: Session, tenant_id: int, data: ExampleCreate) -> Example:
    example = Example(tenant_id=tenant_id, name=data.name)
    db.add(example)
    db.commit()
    db.refresh(example)
    return example

def get_examples(db: Session, tenant_id: int) -> list[Example]:
    return db.query(Example).filter(Example.tenant_id == tenant_id).all()

# api/v1/example.py
from fastapi import APIRouter, Depends, HTTPException
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
    try:
        return example_service.create_example(db, tenant_id, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[ExampleResponse])
async def get_examples(
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    return example_service.get_examples(db, tenant_id)
```

## Questions to Ask

When working on a feature, ask:

1. **Does this need tenant isolation?** (Almost always yes)
2. **Where should this logic live?** (Service layer, not API)
3. **What permissions are needed?** (Public, authenticated, admin)
4. **What errors can occur?** (Handle gracefully)
5. **Does this need async processing?** (Use Celery if long-running)
6. **What data structure is needed?** (Model + schema)
7. **How is this tested?** (Add tests for new features)

## Resources

- **Architecture**: `docs/ARCHITECTURE.md`
- **Getting Started**: `docs/GETTING_STARTED.md`
- **Developer Guide**: `docs/DEVELOPER_GUIDE.md`
- **API Docs**: http://localhost:8000/docs (when running)
- **Code Examples**: Look at existing `workspace.py`, `ingestion.py`, `chat.py`

