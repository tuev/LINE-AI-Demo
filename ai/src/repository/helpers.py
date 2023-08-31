import datetime
from typing import Any, Generator, Generic, TypeVar


T = TypeVar("T")
S = TypeVar("S")


def get_timestamp():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


class GeneratorValue(Generic[T, S]):
    def __init__(self, gen: Generator[T, Any, S]):
        self.gen: Generator[T, Any, S] = gen

    def __iter__(self):
        self.value = yield from self.gen
