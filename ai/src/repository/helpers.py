import datetime
from typing import Generator, List, TypeVar


T = TypeVar("T")
S = TypeVar("S")


def get_timestamp():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


def print_prompt(prompt: str):
    print(">>>")
    print(prompt)
    print("===")


def make_chunks(lst: List[T], n) -> Generator[List[T], None, None]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
