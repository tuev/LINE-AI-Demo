import json
from datetime import datetime
from enum import Enum
from typing import Any, List
from uuid import uuid4
from fastapi import HTTPException, status
from peewee import CharField, DateTimeField, TextField
from pydantic import BaseModel

from repository.auth_repo import LineUserInfo
from repository.base_db import BaseDBModel, VectorField, from_datetime, from_str, get_db
from repository.helpers import cprint_warn, get_timestamp
from repository.llm_facade import LLMFacade
from systems.simple_ai_system import ExtractResult


class UsageTypeEnum(Enum):
    Extract = "extract"

    @staticmethod
    def parse_usage_data(usage_type: "UsageTypeEnum", data: Any) -> ExtractResult:
        if usage_type == UsageTypeEnum.Extract:
            return ExtractResult.parse_obj(data)

        raise Exception("unknown usage_type")


class UsageDb(BaseDBModel):
    usage_id = CharField()
    timestamp = DateTimeField()
    user_id = CharField()
    userdetail = TextField()
    result = TextField()
    result_vector = VectorField(length=1536)
    usage_type = CharField()
    usage_data = TextField()


class UsageUserDetail(BaseModel):
    name: str
    picture: str


class Usage(BaseModel):
    usage_id: str
    timestamp: datetime
    user_id: str
    userdetail: UsageUserDetail
    result: str
    usage_type: UsageTypeEnum
    usage_data: dict

    @staticmethod
    def from_db(db_usage: UsageDb):
        try:
            userdetail = UsageUserDetail.parse_raw(from_str(db_usage.userdetail))
            usage_type = UsageTypeEnum(from_str(db_usage.usage_type))
            usage_data = UsageTypeEnum.parse_usage_data(
                usage_type, json.loads(from_str(db_usage.usage_data))
            )
            return Usage(
                usage_id=from_str(db_usage.usage_id),
                timestamp=from_datetime(db_usage.timestamp),
                user_id=from_str(db_usage.user_id),
                userdetail=userdetail,
                result=from_str(db_usage.result),
                usage_type=usage_type,
                usage_data=usage_data.dict(),
            )
        except Exception as e:
            cprint_warn(f"usage_data corrupted {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="usage_data corrupted",
            )


class UsageRepo:
    def __init__(self, llm: LLMFacade) -> None:
        self._llm = llm

    def _format_usage_result(self, query: str, result: str) -> str:
        return f"QUESTION:\n\n{query}\n---\nANSWER:\n\n{result}\n"

    def create(
        self,
        userdetail: LineUserInfo,
        query: str,
        result: str,
        usage_type: UsageTypeEnum,
        usage_data: dict,
    ):
        usage_id = str(uuid4())
        usage_result = self._format_usage_result(query, result)
        result_vector = self._llm.openai_embeddings(usage_result)
        usage_usage_detail = UsageUserDetail(
            name=userdetail.name, picture=userdetail.picture
        )

        try:
            _usage_data = UsageTypeEnum.parse_usage_data(usage_type, usage_data)
        except Exception as e:
            cprint_warn(str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cannot parse usage data",
            )

        item = UsageDb(
            usage_id=usage_id,
            timestamp=get_timestamp(),
            user_id=userdetail.sub,
            userdetail=usage_usage_detail.json(),
            query=query,
            result=usage_result,
            result_vector=result_vector,
            usage_type=usage_type.value,
            usage_data=_usage_data.json(),
        )
        item.save()
        return item.get_id()

    def list_by_timestamp(self, skip: int, limit: int) -> List[Usage]:
        return [
            Usage.from_db(r)
            for r in (
                UsageDb.select()
                .order_by(UsageDb.timestamp.desc())
                .paginate(skip, limit)
            )
        ]

    def delete_by_id(self, usage_id: str):
        UsageDb.delete().where(UsageDb.usage_id == usage_id).execute()


# Create table if not exists
get_db().create_tables([UsageDb])
