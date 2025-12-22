from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user, get_current_tenant
from app.db.models.user import User, UserRole
from app.schemas.workspace import WorkspaceInfo, WorkspaceMember, WorkspaceJoin, WorkspaceInvite
from app.services.workspace_service import (
    get_workspace_info,
    generate_invite_code,
    join_workspace_by_invite,
    get_workspace_members,
    update_member_role,
    remove_member
)

router = APIRouter()


@router.get("/info", response_model=WorkspaceInfo)
async def get_workspace_info_endpoint(
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    return get_workspace_info(db, tenant_id)


@router.post("/invite-code")
async def generate_invite_code_endpoint(
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    code = generate_invite_code(db, tenant_id, current_user)
    return {"invite_code": code}


@router.post("/join", response_model=dict)
async def join_workspace_endpoint(
    join_data: WorkspaceJoin,
    db: Session = Depends(get_db)
):
    return join_workspace_by_invite(
        db,
        join_data.invite_code,
        join_data.email,
        join_data.name,
        join_data.password
    )


@router.get("/members", response_model=list[WorkspaceMember])
async def get_members_endpoint(
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    members = get_workspace_members(db, tenant_id)
    return [
        {
            "id": m.id,
            "email": m.email,
            "name": m.name,
            "role": m.role.value,
            "created_at": m.created_at
        }
        for m in members
    ]


@router.patch("/members/{user_id}/role")
async def update_member_role_endpoint(
    user_id: int,
    new_role: UserRole,
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    updated_user = update_member_role(db, tenant_id, user_id, new_role, current_user)
    return {
        "id": updated_user.id,
        "email": updated_user.email,
        "role": updated_user.role.value
    }


@router.delete("/members/{user_id}")
async def remove_member_endpoint(
    user_id: int,
    current_user: User = Depends(get_current_user),
    tenant_id: int = Depends(get_current_tenant),
    db: Session = Depends(get_db)
):
    remove_member(db, tenant_id, user_id, current_user)
    return {"message": "Member removed"}

