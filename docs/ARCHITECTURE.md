# Architecture

## Overview

Multi-tenant knowledge platform with RAG query interface and workspace collaboration. Built with FastAPI, PostgreSQL, FAISS, React, and local LLM.

## Project Structure

```
backend/app/
├── api/v1/          # API endpoints
│   ├── auth.py      # Authentication (register, login)
│   ├── workspace.py # Workspace management (invites, members, roles)
│   ├── ingestion.py # Document upload and ingestion
│   ├── chat.py      # RAG query interface
│   ├── users.py     # User management
│   └── tasks.py     # Async task status
├── core/            # Config, security, logging
│   ├── config.py    # Application settings
│   ├── security.py  # JWT, password hashing
│   ├── dependencies.py # FastAPI dependencies (auth, tenant extraction)
│   └── logger.py    # Structured JSON logging
├── db/              # Models, session
│   ├── models/      # SQLAlchemy models
│   │   ├── user.py  # User model with role (ADMIN/MEMBER)
│   │   ├── tenant.py # Tenant/Workspace model with invite_code
│   │   ├── document.py # Document model with versioning
│   │   └── document_chunk.py # Chunk model for vector storage
│   └── session.py   # Database session management
├── services/        # Business logic
│   ├── auth_service.py # Authentication logic
│   ├── workspace_service.py # Workspace management
│   ├── ingestion_service.py # Document processing
│   ├── rag.py       # RAG query logic
│   ├── vector_store.py # FAISS operations
│   └── embedding.py # Text embedding generation
├── tasks/           # Celery async tasks
│   └── ingestion_tasks.py # Background document processing
└── schemas/         # Pydantic models for API
```

```
frontend/
├── src/
│   ├── pages/       # React pages
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Dashboard.jsx
│   │   ├── Documents.jsx
│   │   ├── Query.jsx
│   │   └── Workspace.jsx
│   ├── components/  # Reusable components
│   │   ├── Layout.jsx
│   │   └── ProtectedRoute.jsx
│   └── contexts/    # React context
│       └── AuthContext.jsx
```

## Request Flow

### API Request Flow
```
HTTP Request → FastAPI Router → Dependency Injection (Auth) → Service Layer → Database/FAISS → Response
```

### Frontend Request Flow
```
User Action → React Component → Axios API Call → Backend API → Response → State Update → UI Update
```

## Key Components

### FastAPI
- Web framework with automatic API docs (`/docs`)
- Type validation via Pydantic schemas
- Dependency injection for DB sessions, auth, tenant extraction
- Middleware for metrics and logging

### SQLAlchemy
- ORM for PostgreSQL
- Models in `db/models/`
- Migrations via Alembic
- Relationship management (User ↔ Tenant, Document ↔ Chunk)

### FAISS
- Vector similarity search for RAG
- Per-tenant indices stored on disk
- Efficient similarity search for document chunks

### Celery + Redis
- Async task processing for document ingestion
- Background embedding generation
- Task status tracking

### React Frontend
- Component-based UI with React Router
- Context API for authentication state
- Axios for API communication
- Tailwind CSS for styling

## Multi-Tenancy

### Tenant Isolation
- `tenant_id` extracted from JWT claims
- All database queries filtered by `tenant_id`
- Separate FAISS indices per tenant (`{tenant_id}.index`)
- Redis cache keys prefixed with tenant ID
- Complete data isolation at all layers

### Workspace Management
- **Tenant Creation**: First user to register creates workspace (becomes ADMIN)
- **Invite System**: Admins generate invite codes for workspace access
- **Member Roles**: ADMIN (full access) and MEMBER (standard access)
- **RBAC**: Role-based access control enforced at API layer

## Authentication & Authorization

### JWT Authentication
- Token contains: `user_id`, `tenant_id`, `role`
- Token validation on every protected endpoint
- Automatic tenant extraction from token

### RBAC (Role-Based Access Control)
- **ADMIN**: Can manage workspace (invite members, update roles, remove members)
- **MEMBER**: Can access workspace resources (upload docs, query, view members)
- Role enforcement via `require_admin_role` dependency

## Patterns

### Service Layer Pattern
- Business logic separated from API endpoints
- Services handle data access and business rules
- API endpoints are thin wrappers around services

### Dependency Injection
- FastAPI `Depends()` for DB sessions, auth, tenant extraction
- Reusable dependencies for common operations
- Clean separation of concerns

### Repository Pattern
- Services act as repositories for data access
- Database queries encapsulated in services
- Easy to test and maintain

## Data Flow

### Document Ingestion Flow
```
1. User uploads document → API endpoint
2. Document saved to storage → PostgreSQL metadata
3. Async Celery task triggered
4. Document chunked → Embeddings generated → FAISS index updated
5. Task status tracked in Redis
```

### Query Flow
```
1. User submits query → API endpoint
2. Query embedded → FAISS similarity search (tenant-scoped)
3. Top-k chunks retrieved → LLM context generation
4. LLM generates answer → Response returned
```

## Extending

### Adding a New API Endpoint
1. Create Pydantic schema in `schemas/`
2. Create service function in `services/`
3. Add API endpoint in `api/v1/`
4. Register router in `main.py`

### Adding a New Frontend Page
1. Create page component in `frontend/src/pages/`
2. Add route in `frontend/src/App.jsx`
3. Add navigation link in `Layout.jsx`

### Adding a New Database Model
1. Create SQLAlchemy model in `db/models/`
2. Import in `db/models/__init__.py`
3. Create Alembic migration: `alembic revision --autogenerate -m "description"`
4. Apply migration: `alembic upgrade head`

## Security Considerations

- JWT tokens expire after 24 hours (configurable)
- Passwords hashed with bcrypt
- Tenant isolation enforced at all layers
- RBAC prevents unauthorized access
- Input validation via Pydantic schemas
- SQL injection prevented by SQLAlchemy ORM

## Performance Considerations

- Async document processing prevents blocking
- FAISS provides fast vector similarity search
- Redis caching for frequently accessed data
- Database indexes on `tenant_id` and `email`
- Connection pooling for database connections
