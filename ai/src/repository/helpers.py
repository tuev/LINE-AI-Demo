import datetime
import os
from typing import Generator, List, TypeVar
from langchain.schema import BaseMessage
import tiktoken


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


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def messages_to_str(msg: List[BaseMessage]):
    return "\n".join([f"{m.type}:{m.content}" for m in msg])


class bcolors:
    HEADER = "\033[95m"
    OKORANGE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def cprint(text: str, color):
    if os.getenv("LOCAL") is not None:
        with open("./log.out", "a") as f:
            f.write(text + "\n")

        print(color + text + bcolors.ENDC)


def cprint_warn(text: str):
    cprint(text, bcolors.WARNING)


def cprint_debug(text: str):
    cprint(text, bcolors.FAIL)


def cprint_green(text: str):
    cprint(text, bcolors.OKGREEN)


def cprint_orange(text: str):
    cprint(text, bcolors.OKORANGE)


def cprint_cyan(text: str):
    cprint(text, bcolors.OKCYAN)
