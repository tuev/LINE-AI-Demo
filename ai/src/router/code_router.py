import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from repository import auth_repo, code_repo, request_record_repo
from sse_starlette.sse import EventSourceResponse
from repository import usage_repo

from repository.auth_repo import LineUserInfo
from repository.code_repo import ChatModelEnum
from repository.llm_facade import LLMFinalContent


code_router = APIRouter(prefix="/code")


class CompletionStream(BaseModel):
    query: str


@code_router.post("/completion_stream")
async def completion_stream(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    body: CompletionStream,
):
    user_request_record = request_record_repo.get_by_user(user.sub)

    if user_request_record is not None:
        time_elapsed = datetime.datetime.now() - user_request_record.timestamp
        print(time_elapsed)

        RATE_LIMIT_SECONDS = 30

        if time_elapsed < datetime.timedelta(seconds=RATE_LIMIT_SECONDS):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Rate limited: must not more "
                    f"than one request per {RATE_LIMIT_SECONDS} seconds."
                ),
            )

    request_record_repo.create(user.sub)

    async def event_generator():
        for content in code_repo.completion(body.query):
            yield dict(retry=1500, data=content.json())
            if isinstance(content, LLMFinalContent):
                usage_repo.create(
                    user_id=user.sub,
                    userdetail=user,
                    query=body.query,
                    result=content.final_content,
                    usage=content.usage,
                )

    return EventSourceResponse(event_generator())


@code_router.post("/internal_chat")
async def internal_chat(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
):
    internal_token = auth_repo.get_token(user.sub)
    code_repo.internal_chat(ChatModelEnum.Chat_3_5, internal_token)
    return None
