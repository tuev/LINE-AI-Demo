from peewee import CharField, DateTimeField, TextField

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


# Create table if not exists
get_db().create_tables([Usage])
