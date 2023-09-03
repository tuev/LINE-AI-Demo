from peewee import CharField, DateTimeField
from repository.base_db import BaseDBModel, get_db
from repository.helpers import get_timestamp


class RequestRecord(BaseDBModel):
    user_id = CharField()
    timestamp = DateTimeField()


class RequestRecordRepo:
    def create(self, user_id: str):
        item = RequestRecord(
            user_id=user_id,
            timestamp=get_timestamp(),
        )
        item.save()
        return item

    def get_by_user(self, user_id: str) -> RequestRecord | None:
        items = list(
            RequestRecord.select()
            .where(
                RequestRecord.user_id == user_id,
            )
            .order_by(RequestRecord.timestamp.desc())
        )
        if len(items) > 0:
            return items[0]

        return None


# Create table if not exists
get_db().create_tables([RequestRecord])
