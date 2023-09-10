from typing import Annotated, List
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from pydantic import BaseModel


from repository import auth_repo, simple_ai_system
from repository.auth_repo import LineUserInfo

ai_router = APIRouter(prefix="/ai")


class SimpleExtract(BaseModel):
    documents: List[str]
    question: str


@ai_router.post("/simple_extract")
def simple_extract(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    body: SimpleExtract,
):
    internal_token = auth_repo.get_token(user.sub)
    if internal_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="internal token not found",
        )

    if internal_token.is_expired():
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="unable to proceed because the internal token is about to expire.",
        )

    result = simple_ai_system.extract(
        internal_token.token, body.question, body.documents
    )

    return result
