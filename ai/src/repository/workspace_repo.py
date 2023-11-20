from datetime import datetime
from enum import StrEnum
from uuid import uuid4
from peewee import CharField, DateTimeField
from pydantic import BaseModel
from repository.base_db import BaseDBModel, from_datetime, from_str, get_db
from repository.helpers import get_timestamp


class WorkspaceDb(BaseDBModel):
    workspace_id = CharField(unique=True)
    name = CharField()
    owner_id = CharField()
    create_at = DateTimeField()


class Workspace(BaseModel):
    workspace_id: str
    name: str
    owner_id: str
    create_at: datetime

    def to_db(self) -> WorkspaceDb:
        return WorkspaceDb(
            workspace_id=self.workspace_id,
            name=self.name,
            owner_id=self.owner_id,
            create_at=self.create_at,
        )

    @staticmethod
    def from_db(db_model: WorkspaceDb):
        return Workspace(
            workspace_id=from_str(db_model.workspace_id),
            name=from_str(db_model.name),
            owner_id=from_str(db_model.owner_id),
            create_at=from_datetime(db_model.create_at),
        )


class WorkspaceMemberTypeEnum(StrEnum):
    CoOwner = "co-owner"
    Member = "member"
    ReadOnly = "read-only"


class WorkspaceMemberDb(BaseDBModel):
    relation_id = CharField(unique=True)
    workspace_id = CharField()
    member_id = CharField()
    member_type = CharField()


class WorkspaceMember(BaseModel):
    relation_id: str
    workspace_id: str
    member_id: str
    member_type: WorkspaceMemberTypeEnum

    def to_db(self) -> WorkspaceMemberDb:
        return WorkspaceMemberDb(
            relation_id=self.relation_id,
            workspace_id=self.workspace_id,
            member_id=self.member_id,
            member_type=self.member_type,
        )

    @staticmethod
    def from_db(db_model: WorkspaceMemberDb):
        return WorkspaceMember(
            relation_id=from_str(db_model.relation_id),
            workspace_id=from_str(db_model.workspace_id),
            member_id=from_str(db_model.member_id),
            member_type=WorkspaceMemberTypeEnum(from_str(db_model.member_type)),
        )


class WorkspaceRepo:
    def __init__(self) -> None:
        pass

    def get_workspace_by_owner(self, user_id: str, workspace_id: str):
        workspace_db = WorkspaceDb.get_or_none(
            WorkspaceDb.workspace_id == workspace_id,
            WorkspaceDb.owner_id == user_id,
        )
        if workspace_db is None:
            return None

        return Workspace.from_db(workspace_db)

    def create_workspace(self, user_id: str, name: str):
        workspace = Workspace(
            workspace_id=str(uuid4()),
            owner_id=user_id,
            name=name,
            create_at=get_timestamp(),
        )
        workspace.to_db().save()
        return workspace

    def delete_workspace(self, workspace_id: str):
        WorkspaceDb.delete().where(
            WorkspaceDb.workspace_id == workspace_id,
        ).execute()

    def update_workspace(self, workspace: Workspace):
        WorkspaceDb.update(
            {
                WorkspaceDb.name: workspace.name,
            }
        ).where(
            WorkspaceDb.workspace_id == workspace.workspace_id,
        ).execute()

    def transfer_owner(self, workspace: Workspace):
        WorkspaceDb.update(
            {
                WorkspaceDb.owner_id: workspace.owner_id,
            }
        ).where(
            WorkspaceDb.workspace_id == workspace.workspace_id,
        ).execute()

    def list_workspaces_by_owner(self, user_id: str):
        workspaces = (
            WorkspaceDb.select()
            .where(
                WorkspaceDb.owner_id == user_id,
            )
            .execute()
        )
        return [Workspace.from_db(workspace) for workspace in workspaces]

    def upsert_workspace_member(
        self, workspace_id: str, member_id: str, member_type: WorkspaceMemberTypeEnum
    ):
        workspace_member = WorkspaceMember(
            relation_id=f"{workspace_id}/{member_id}",
            workspace_id=workspace_id,
            member_id=member_id,
            member_type=member_type,
        )
        WorkspaceMemberDb.insert(workspace_member.dict()).on_conflict(
            conflict_target=[WorkspaceMemberDb.relation_id],
            update=workspace_member.dict(),
        ).execute()
        return workspace_member

    def remove_workspace_member(self, workspace_id: str, member_id: str):
        WorkspaceMemberDb.delete().where(
            WorkspaceMemberDb.workspace_id == workspace_id,
            WorkspaceMemberDb.member_id == member_id,
        ).execute()

    def remove_all_worksace_members(self, workspace_id: str):
        WorkspaceMemberDb.delete().where(
            WorkspaceMemberDb.workspace_id == workspace_id
        ).execute()

    def list_workspace_members(self, workspace_id: str):
        workspace_members = (
            WorkspaceMemberDb.select()
            .where(
                WorkspaceMemberDb.workspace_id == workspace_id,
            )
            .execute()
        )
        return [WorkspaceMember.from_db(member) for member in workspace_members]


# Create table if not exists
get_db().create_tables([WorkspaceDb, WorkspaceMemberDb])
