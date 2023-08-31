from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from repository import auth_repo, code_repo
from sse_starlette.sse import EventSourceResponse
from repository import usage_repo

from repository.auth_repo import LineUserInfo
from repository.helpers import GeneratorValue


code_router = APIRouter(prefix="/code")


@code_router.get("/health")
def health():
    return "ok"


class CompletionStream(BaseModel):
    query: str


@code_router.post("/completion_stream")
async def completion_stream(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    body: CompletionStream,
):
    async def event_generator():
        gen = GeneratorValue(code_repo.completion(body.query))
        for content in gen:
            content = content.get("content")
            yield content

        result, usage = gen.value

        usage_repo.create(
            user_id=user.sub,
            userdetail=user,
            query=body.query,
            result=result,
            usage=usage,
        )

    return EventSourceResponse(event_generator())
