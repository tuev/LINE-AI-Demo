import datetime
from typing import TypeVar


T = TypeVar("T")
S = TypeVar("S")


def get_timestamp():
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


def print_prompt(prompt: str):
    print(">>>")
    print(prompt)
    print("===")
