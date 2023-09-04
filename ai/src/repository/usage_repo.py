from datetime import datetime, timezone
import json
from typing import List
from peewee import CharField, DateTimeField, TextField
from pydantic import BaseModel

from repository.auth_repo import LineUserInfo
from repository.base_db import BaseDBModel, get_db
from repository.helpers import get_timestamp
from repository.llm_facade import LLMUsage


class Usage(BaseDBModel):
    user_id = CharField()
    userdetail = TextField()
    query = TextField()
    result = TextField()
    usage = TextField(null=True)
    timestamp = DateTimeField()


class UsageUserDetail(BaseModel):
    name: str
    picture: str
    timestamp: datetime


class UsageRepo:
    def create(
        self,
        user_id: str,
        userdetail: LineUserInfo,
        query: str,
        result: str,
        usage: LLMUsage | None,
    ):
        item = Usage(
            user_id=user_id,
            userdetail=userdetail.json(),
            query=query,
            result=result,
            usage=usage.json() if usage is not None else None,
            timestamp=get_timestamp(),
        )
        item.save()
        return item.get_id()

    def last_usages(self, amount=10) -> List[UsageUserDetail]:
        results: List[UsageUserDetail] = []
        for result in (
            Usage.select(Usage.userdetail, Usage.timestamp)
            .order_by(Usage.timestamp.desc())
            .limit(amount)
        ):
            userdetail = json.loads(result.userdetail)
            results.append(
                UsageUserDetail(
                    name=userdetail.get("name"),
                    picture=userdetail.get("picture"),
                    timestamp=result.timestamp.replace(tzinfo=timezone.utc),
                )
            )

        return results


# Create table if not exists
get_db().create_tables([Usage])
