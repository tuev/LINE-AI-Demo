from datetime import datetime
from typing import List, TypeVar

import yaml
from pydantic import BaseModel
from repository.document_repo import Document, DocumentRepo
from repository.helpers import cprint_cyan, cprint_green, get_timestamp, messages_to_str
from repository.llm_facade import ChatModelEnum, LLMFacade
from repository.vector_store_repo import (
    VectorMetadata,
    VectorQueryResult,
    VectorStoreRepo,
)

from systems.base_ai_ystem import BaseAISystem

T = TypeVar("T")


class ExtractResultReference(BaseModel):
    namespace: str
    doc_id: str
    filename: str
    metadata: VectorMetadata
    similarity: float
    upload_by: str
    upload_at: datetime

    @staticmethod
    def from_reference(doc: Document, reference: VectorQueryResult):
        return ExtractResultReference(
            namespace=doc.namespace,
            doc_id=doc.doc_id,
            filename=doc.filename,
            metadata=reference.metadata,
            similarity=reference.similarity,
            upload_by=doc.upload_by,
            upload_at=doc.upload_at,
        )


class ExtractResult(BaseModel):
    question: str
    result: str
    references: List[ExtractResultReference]
    duration_ms: int
    timestamp: datetime


class SimpleAISystem:
    def __init__(
        self,
        llm: LLMFacade,
        document_repo: DocumentRepo,
        vector_store_repo: VectorStoreRepo,
    ):
        self._llm = llm
        self._document_repo = document_repo
        self._vector_store_repo = vector_store_repo

        with open("/app/src/prompts/simple.yaml") as f:
            config = yaml.safe_load(f)

        self._extract_prompt = BaseAISystem.load_messages(config, "Extract")

    def _get_result_references(
        self, references: List[VectorQueryResult]
    ) -> List[ExtractResultReference]:
        doc_ids = [r.document for r in references]
        docs = {}
        for d in self._document_repo.get_docs_or_raise_not_found(doc_ids):
            docs[d.doc_id] = d

        return [
            ExtractResultReference.from_reference(docs[ref.document], ref)
            for ref in references
        ]

    def extract(self, question: str, documents: List[str]) -> ExtractResult:
        start_ts = get_timestamp()
        query_vector = self._llm.openai_embeddings(question)
        references = self._vector_store_repo.similarity_search_by_documents(
            query_vector, documents, limit=5
        )
        result_references = self._get_result_references(references)

        information_str = ""
        for r in result_references:
            title = r.filename
            content = r.metadata.content
            information_str += "\n---\n" + f"# Document: {title}\n\n{content}\n"

        messages_prompt = self._extract_prompt.format_prompt(
            information=information_str,
            question=question,
        ).to_messages()
        cprint_green(messages_to_str(messages_prompt))

        chat = self._llm.create_chat(ChatModelEnum.Chat_4, temperature=0.1)
        planning_res = chat(messages_prompt).content

        cprint_cyan(planning_res)
        cprint_cyan("-" * 80)

        end_ts = get_timestamp()

        return ExtractResult(
            question=question,
            result=planning_res,
            references=result_references,
            duration_ms=int((start_ts - end_ts).microseconds / 1000),
            timestamp=get_timestamp(),
        )
