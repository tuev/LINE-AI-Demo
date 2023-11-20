from typing import Annotated, List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel
from repository import auth_repo, workspace_repo
from repository.auth_repo import LineUserInfo
from repository.workspace_repo import WorkspaceMemberTypeEnum

workspace_router = APIRouter(prefix="/workspaces")


class CreateWorkspace(BaseModel):
    name: str


@workspace_router.post("")
def create_workspace(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    body: CreateWorkspace,
):
    new_workspace = workspace_repo.create_workspace(user_id=user.sub, name=body.name)
    return new_workspace


def _get_workspace_or_forbidden(user_id: str, workspace_id: str):
    workspace = workspace_repo.get_workspace_by_owner(
        user_id=user_id, workspace_id=workspace_id
    )

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not the owner of this workspace",
        )
    return workspace


@workspace_router.get("")
def get_user_workspace(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
):
    return workspace_repo.list_workspaces_by_owner(user_id=user.sub)


@workspace_router.delete("/{workspace_id}")
def delete_workspace(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    workspace_id: str,
):
    _get_workspace_or_forbidden(user.sub, workspace_id)
    # TODO: Verify if exist questions and documents

    workspace_repo.remove_all_worksace_members(workspace_id=workspace_id)
    workspace_repo.delete_workspace(workspace_id=workspace_id)

    return workspace_id


class UpdateWorkspace(BaseModel):
    name: str


@workspace_router.put("/{workspace_id}")
def update_workspace(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    workspace_id: str,
    body: UpdateWorkspace,
):
    workspace = _get_workspace_or_forbidden(user.sub, workspace_id)
    workspace.name = body.name
    workspace_repo.update_workspace(workspace)
    return workspace


class UpdateWorkspaceOwner(BaseModel):
    new_owner_id: str


@workspace_router.put("/{workspace_id}/owner")
def update_workspace_owner(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    workspace_id: str,
    body: UpdateWorkspaceOwner,
):
    workspace = _get_workspace_or_forbidden(user.sub, workspace_id)
    workspace.owner_id = body.new_owner_id
    workspace_repo.transfer_owner(workspace)
    return workspace


class AddMemberDatum(BaseModel):
    member_id: str
    member_type: WorkspaceMemberTypeEnum


class AddMembers(BaseModel):
    members: List[AddMemberDatum]


@workspace_router.post("/{workspace_id}/members")
def add_members(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    workspace_id: str,
    body: AddMembers,
):
    _get_workspace_or_forbidden(user.sub, workspace_id)
    found_members = auth_repo.get_users([m.member_id for m in body.members])
    found_member_ids = [m.sub for m in found_members]
    for member_req in body.members:
        if (member_req.member_id in found_member_ids) is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"not found member {member_req.member_id}",
            )

    new_workspace_members = []
    for member_req in body.members:
        new_workspace_members.append(
            workspace_repo.upsert_workspace_member(
                workspace_id=workspace_id,
                member_id=member_req.member_id,
                member_type=member_req.member_type,
            )
        )

    return new_workspace_members


class RemoveMembers(BaseModel):
    member_ids: List[str]


@workspace_router.delete("/{workspace_id}/members")
def remove_members(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    workspace_id: str,
    body: RemoveMembers,
):
    _get_workspace_or_forbidden(user.sub, workspace_id)

    workspace_members = workspace_repo.list_workspace_members(workspace_id=workspace_id)
    workspace_member_ids = list(map(lambda m: m.member_id, workspace_members))

    for member_id in body.member_ids:
        if member_id in workspace_member_ids is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"not found member {member_id} in workspace",
            )

    for member_id in body.member_ids:
        workspace_repo.remove_workspace_member(
            workspace_id=workspace_id,
            member_id=member_id,
        )

    return workspace_member_ids


@workspace_router.get("/{workspace_id}/members")
def list_all_members(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    workspace_id: str,
):
    _get_workspace_or_forbidden(user.sub, workspace_id)
    members = workspace_repo.list_workspace_members(workspace_id=workspace_id)
    members_details = auth_repo.get_users(list(map(lambda m: m.member_id, members)))
    return [
        {
            "member_id": member.member_id,
            "member_type": member.member_type,
            "user_detail": {
                "name": detail.name,
                "picture": detail.picture,
            },
        }
        for member, detail in zip(members, members_details)
    ]
