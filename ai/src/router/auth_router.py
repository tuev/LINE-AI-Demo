from fastapi import APIRouter
from pydantic import BaseModel
from repository import auth_repo


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
