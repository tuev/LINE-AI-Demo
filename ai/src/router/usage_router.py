from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from repository import usage_repo
from repository import auth_repo
from repository.auth_repo import LineUserInfo
from repository.usage_repo import UsageTypeEnum


usage_router = APIRouter(prefix="/usage")


class RecordUsage(BaseModel):
    query: str
    result: str
    usage_type: UsageTypeEnum
    usage_data: dict


@usage_router.post("/record")
async def record_usage(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    body: RecordUsage,
):
    usage_repo.create(
        userdetail=user,
        query=body.query,
        result=body.result,
        usage_type=body.usage_type,
        usage_data=body.usage_data,
    )
    return "success"


@usage_router.get("/list_by_timestamp/")
async def list_by_timestamp(
    skip: int = 0,
    limit: int = 10,
):
    res = usage_repo.list_by_timestamp(skip, limit)
    return res


@usage_router.delete("/delete/{usage_id}")
async def delete_by_usage_id(usage_id: str):
    usage_repo.delete_by_id(usage_id)
    return "success"
