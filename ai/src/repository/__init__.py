import os

from dotenv import load_dotenv

from repository.auth_repo import AuthRepo
from repository.code_repo import CodeRepo
from repository.llm_facade import LLMFacade
from repository.request_record_repo import RequestRecordRepo
from repository.usage_repo import UsageRepo

load_dotenv()

LLM_ENDPOINT = os.environ["LLM_ENDPOINT"]
LIFF_CLIENT_ID = os.environ["LIFF_CLIENT_ID"]

llm_facade = LLMFacade(LLM_ENDPOINT)

auth_repo = AuthRepo(client_id=LIFF_CLIENT_ID)
code_repo = CodeRepo(llm=llm_facade)
usage_repo = UsageRepo()
request_record_repo = RequestRecordRepo()

__all__ = ["auth_repo", "code_repo", "usage_repo"]
