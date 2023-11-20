import os

from dotenv import load_dotenv
from minio import Minio
from systems.simple_ai_system import SimpleAISystem

from repository.auth_repo import AuthRepo
from repository.document_download import DocumentDownload
from repository.document_parser import DocumentParser
from repository.document_repo import DocumentRepo
from repository.llm_facade import LLMFacade
from repository.storage_facade import StorageFacade
from repository.usage_repo import UsageRepo
from repository.vector_store_repo import VectorStoreRepo
from repository.workspace_repo import WorkspaceRepo

load_dotenv()

S3_ENDPOINT = os.environ["S3_ENDPOINT"]
S3_ACCESS_KEY = os.environ["S3_ACCESS_KEY"]
S3_SECRET_KEY = os.environ["S3_SECRET_KEY"]
S3_REGION = os.environ["S3_REGION"]
LIFF_CLIENT_ID = os.environ["LIFF_CLIENT_ID"]
UNSTRUCTURED_ENDPOINT = os.environ["UNSTRUCTURED_ENDPOINT"]
SUPPORT_TYPES = os.environ["SUPPORT_TYPES"]
OPENAI_KEY = os.environ["OPENAI_KEY"]

minio_client = Minio(
    S3_ENDPOINT,
    access_key=S3_ACCESS_KEY,
    secret_key=S3_SECRET_KEY,
    region=S3_REGION,
    secure=False,
)

llm_facade = LLMFacade(OPENAI_KEY)
document_parser = DocumentParser(UNSTRUCTURED_ENDPOINT, SUPPORT_TYPES)

auth_repo = AuthRepo(client_id=LIFF_CLIENT_ID)
usage_repo = UsageRepo(llm=llm_facade)
vector_store_repo = VectorStoreRepo(table_name="vectorstore", vector_size=1536)
storage_facade = StorageFacade(minio_client, "lvn-ai-demo")
document_repo = DocumentRepo(
    llm=llm_facade,
    vector_store_repo=vector_store_repo,
    storage_facade=storage_facade,
    document_parser=document_parser,
)
document_download = DocumentDownload()
simple_ai_system = SimpleAISystem(llm_facade, document_repo, vector_store_repo)
workspace_repo = WorkspaceRepo()

__all__ = [
    "auth_repo",
    "usage_repo",
    "vector_store_repo",
    "document_repo",
    "simple_ai_system",
]
