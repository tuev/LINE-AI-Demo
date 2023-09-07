import os

from dotenv import load_dotenv

from repository.auth_repo import AuthRepo
from repository.base_db import get_db
from repository.code_repo import CodeRepo
from repository.llm_facade import LLMFacade
from repository.request_record_repo import RequestRecordRepo
from repository.usage_repo import UsageRepo
from repository.vector_store_repo import VectorStoreRepo


load_dotenv()

LLM_ENDPOINT = os.environ["LLM_ENDPOINT"]
LIFF_CLIENT_ID = os.environ["LIFF_CLIENT_ID"]

llm_facade = LLMFacade(LLM_ENDPOINT)

auth_repo = AuthRepo(client_id=LIFF_CLIENT_ID)
code_repo = CodeRepo(llm=llm_facade)
usage_repo = UsageRepo()
request_record_repo = RequestRecordRepo()
vector_store_repo = VectorStoreRepo(get_db, table_name="vectorstore", vector_size=768)

__all__ = ["auth_repo", "code_repo", "usage_repo", "vector_store_repo"]
