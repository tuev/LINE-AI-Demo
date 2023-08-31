import os

from dotenv import load_dotenv

from repository.auth_repo import AuthRepo
from repository.code_repo import CodeRepo
from repository.llm_facade import LLMFacade
from repository.usage_repo import UsageRepo

load_dotenv()

LLM_ENDPOINT = os.environ["LLM_ENDPOINT"]
llm_facade = LLMFacade(LLM_ENDPOINT)

auth_repo = AuthRepo()
code_repo = CodeRepo(llm=llm_facade)
usage_repo = UsageRepo()

__all__ = ["auth_repo", "code_repo", "usage_repo"]
