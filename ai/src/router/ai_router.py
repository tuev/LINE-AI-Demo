from typing import Annotated, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel


from repository import auth_repo, simple_ai_system
from repository.auth_repo import LineUserInfo, check_token_expired

ai_router = APIRouter(prefix="/ai")


class SimpleExtract(BaseModel):
    documents: List[str]
    question: str


@ai_router.post("/simple_extract")
def simple_extract(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    body: SimpleExtract,
):
    result = simple_ai_system.extract(
        body.question, body.documents
    )

    return result
