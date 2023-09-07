from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from repository import auth_repo
from repository.auth_repo import LineUserInfo


auth_router = APIRouter(prefix="/auth")


class VerifyAccessToken(BaseModel):
    token: str


@auth_router.post("/verify_access_token")
async def verify_access_token(body: VerifyAccessToken):
    return auth_repo.verify_access_token(body.token)


class VerifyIdToken(BaseModel):
    token: str


@auth_router.post("/verify_id_token")
async def verify_id_token(body: VerifyIdToken):
    return auth_repo.verify_id_token(body.token)


class SetInternalToken(BaseModel):
    token: str


@auth_router.post("/set_internal_token")
async def set_internal_token(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    body: SetInternalToken,
):
    auth_repo.set_internal_token(user_id=user.sub, token=body.token)
    return "success"


@auth_router.get("/internal_token_timestamp")
async def internal_token_timestamp(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
):
    return auth_repo.get_token_timestamp(user_id=user.sub)
