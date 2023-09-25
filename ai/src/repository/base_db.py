from datetime import datetime, timezone
from typing import Any, List
from peewee import Field, Model, PostgresqlDatabase
from pgvector.psycopg2 import register_vector


def get_db():
    return PostgresqlDatabase(
        "line-ai-demo",
        user="root",
        password="password",
        host="database",
        port=5432,
    )


register_vector(get_db())


class BaseDBModel(Model):
    class Meta:
        database = get_db()


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_datetime(x: Any) -> datetime:
    assert isinstance(x, datetime)
    return x.replace(tzinfo=timezone.utc)


class VectorField(Field):
    field_type = "vector"

    def __init__(self, length=1536, *args, **kwargs):
        self.length = length
        super(VectorField, self).__init__(*args, **kwargs)

    def db_value(self, value: List[float]):
        return value

    def python_value(self, value: List[float]):
        return value

    def get_modifiers(self):
        return self.length and [self.length] or None
