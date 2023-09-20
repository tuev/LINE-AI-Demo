import multiprocessing
from datetime import datetime
from enum import Enum
from typing import Any, BinaryIO, List
from uuid import uuid4
from fastapi import HTTPException, status
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from peewee import CharField, DateTimeField, IntegerField, TextField
from pydantic import BaseModel
import numpy as np
import yaml

from repository.base_db import (
    BaseDBModel,
    VectorField,
    from_datetime,
    from_int,
    from_str,
    get_db,
)
from repository.document_parser import DocumentParseResult, DocumentParser
from repository.helpers import cprint_cyan, cprint_green, get_timestamp
from repository.llm_facade import ChatModelEnum, LLMFacade
from repository.storage_facade import StorageFacade
from repository.db_connect_base import DbConnectBase
from repository.vector_store_repo import VectorStoreRepo

from sklearn.cluster import KMeans

from systems.base_ai_ystem import BaseAISystem


class DocumentDB(BaseDBModel):
    namespace = CharField()
    doc_id = CharField(unique=True)
    filename = CharField()
    content_type = CharField()
    bytesize = IntegerField()  # NOTE: IntegerField limit is 2147483648 ~ 2GB
    upload_by = CharField()
    upload_at = DateTimeField()
    summary = TextField()
    process_status = CharField()
    visibility = CharField()
    embeddings = VectorField(length=768, null=True)


class DocumentProcessStatusEnum(Enum):
    Uploaded = "upload"
    Processing = "processing"
    Error = "error"
    Processed = "processed"


class DocumentVisibilityEnum(Enum):
    Public = "public"
    Private = "private"
    Link = "link"


class Document(BaseModel):
    namespace: str
    doc_id: str
    filename: str
    content_type: str
    bytesize: int
    upload_by: str
    upload_at: datetime
    summary: str
    process_status: DocumentProcessStatusEnum
    visibility: DocumentVisibilityEnum

    def to_db(self) -> DocumentDB:
        return DocumentDB(
            namespace=self.namespace,
            doc_id=self.doc_id,
            filename=self.filename,
            content_type=self.content_type,
            bytesize=self.bytesize,
            upload_by=self.upload_by,
            upload_at=self.upload_at,
            summary=self.summary,
            process_status=self.process_status.value,
            visibility=self.visibility.value,
        )

    @staticmethod
    def from_db(db_document: DocumentDB):
        upload_at: Any = db_document.upload_at
        return Document(
            namespace=from_str(db_document.namespace),
            doc_id=from_str(db_document.doc_id),
            filename=from_str(db_document.filename),
            content_type=from_str(db_document.content_type),
            bytesize=from_int(db_document.bytesize),
            upload_by=from_str(db_document.upload_by),
            upload_at=from_datetime(upload_at),
            summary=from_str(db_document.summary),
            process_status=DocumentProcessStatusEnum(db_document.process_status),
            visibility=DocumentVisibilityEnum(db_document.visibility),
        )


def get_closest_indices(vectors: List[List[float]], num_clusters: int, kmeans: KMeans):
    closest_indices: List[int] = []

    # Loop through the number of clusters you have
    for i in range(num_clusters):
        # Get the list of distances from that particular cluster center
        distances = np.linalg.norm(vectors - kmeans.cluster_centers_[i], axis=1)

        # Find the list position of the closest one (using argmin to find the smallest distance)
        closest_index = np.argmin(distances)

        # Append that position to your closest indices list
        closest_indices.append(int(closest_index))

    return closest_indices


def multiprocessing_document(llm: LLMFacade, doc: DocumentParseResult):
    print(">> Processing", doc.metadata)
    return llm.line_embeddings(doc.text)


class DocumentRepo(DbConnectBase):
    _EMBEDDING_NAMESPACE = "document"
    _CHUNK_SIZE = 1000
    _CHUNK_OVERLAP = 200
    _BUCKET_NAME = "document"

    MAX_PART_SIZE = 30 * 1024 * 1024
    MAX_SIZE_TEXT = "30MB"

    def __init__(
        self,
        llm: LLMFacade,
        document_parser: DocumentParser,
        vector_store_repo: VectorStoreRepo,
        storage_facade: StorageFacade,
    ):
        self._llm = llm
        self._document_parser = document_parser
        self._vector_store_repo = vector_store_repo
        self._storage_facade = storage_facade

        with open("/app/src/prompts/simple.yaml") as f:
            config = yaml.safe_load(f)

        self._summary_prompt = BaseAISystem.load_messages_chat(config, "Summary")
        self._summary_all_prompt = BaseAISystem.load_messages_chat(config, "SummaryAll")

    def get_doc_or_not_found(self, id: str) -> Document:
        item = DocumentDB.get_or_none(DocumentDB.doc_id == id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="not found document"
            )

        return item

    def create(
        self,
        namespace: str,
        filename: str,
        upload_by: str,
        content_type: str,
        blob: BinaryIO,
        bytesize: int,
        visibility: DocumentVisibilityEnum,
    ):
        doc_id = str(uuid4())
        self._storage_facade.upload(
            object_name=doc_id,
            content_type=content_type,
            part_size=self.MAX_PART_SIZE,
            blob=blob,
        )
        item = Document(
            namespace=namespace,
            doc_id=doc_id,
            filename=filename,
            content_type=content_type,
            bytesize=bytesize,
            upload_by=upload_by,
            upload_at=get_timestamp(),
            summary="",
            process_status=DocumentProcessStatusEnum.Uploaded,
            visibility=visibility,
        )
        item.to_db().save()
        return doc_id

    def get_file_or_not_found(self, doc_id: str):
        blob = self._storage_facade.get(doc_id)
        if blob is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="not found document file",
            )

        return blob

    def _get_document_embbedings(self, doc_results: List[str]) -> List[List[float]]:
        doc_embeddings: List[List[float]] = []
        with multiprocessing.Pool(processes=5) as pool:
            workers = [
                pool.apply_async(self._llm.line_embeddings, (doc,))
                for doc in doc_results
            ]
            for result in workers:
                doc_embeddings.append(result.get())

        return doc_embeddings

    def _get_document_cluster_for_summary(self, doc_embeddings: List[List[float]]):
        num_clusters = min(len(doc_embeddings), 5)
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init="auto").fit(
            doc_embeddings
        )
        closest_indices = get_closest_indices(doc_embeddings, num_clusters, kmeans)
        closest_indices = sorted(closest_indices)
        return closest_indices

    def _get_summary_of_text(self, internal_token: str, text: str):
        messages = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(self._summary_prompt),
                HumanMessagePromptTemplate.from_template("{text}\n\nSUMMARY:"),
            ]
        )
        summary = self._llm.internal_chat(
            model=ChatModelEnum.Chat_4,
            internal_token=internal_token,
            messages=messages.format_prompt(text=text).to_messages(),
        )
        return summary

    def _get_combined_summary(self, internal_token: str, texts: List[str]):
        messages = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(self._summary_all_prompt),
                HumanMessagePromptTemplate.from_template("{text}\n\nFULL SUMMARY:"),
            ]
        )
        combined_summary_list = "\n---\n".join(texts)
        summary_all = self._llm.internal_chat(
            model=ChatModelEnum.Chat_4,
            internal_token=internal_token,
            messages=messages.format_prompt(text=combined_summary_list).to_messages(),
        )
        return summary_all

    def process_vector_and_summary(self, internal_token: str, doc_id: str):
        data = self.get_file_or_not_found(doc_id)
        item = self.get_doc_or_not_found(id=doc_id)

        process_status: DocumentProcessStatusEnum = DocumentProcessStatusEnum.Processing

        cprint_cyan(f"Processing {doc_id}")
        DocumentDB.update(
            {
                DocumentDB.process_status: process_status.value,
            }
        ).where(DocumentDB.doc_id == doc_id).execute()

        summary_all = ""
        embeddings: List[float] = []

        try:
            unstructured_docs = self._document_parser.call_unstructured_api(
                document_id=item.doc_id, file_bytes=data, content_type=item.content_type
            )
            doc_results = self._document_parser.simple_parse(unstructured_docs)

            # TODO: Improve the combination of document because information may be
            # in the 300 length docs
            doc_results = list(filter(lambda d: len(d.text) > 300, doc_results))

            doc_embeddings = self._get_document_embbedings(
                list(map(lambda d: d.text, doc_results))
            )

            closest_indices = self._get_document_cluster_for_summary(doc_embeddings)

            summaries: List[str] = []
            for i in closest_indices:
                doc_result = doc_results[i]
                summary = self._get_summary_of_text(internal_token, doc_result.text)
                cprint_green(f"{doc_id} >>> index {i} >>>")
                cprint_green(summary)
                cprint_green("=" * 80)
                summaries.append(summary)

            summary_all = self._get_combined_summary(internal_token, summaries)
            embeddings = self._llm.line_embeddings(summary_all)

            # Clean up existing vectors for idempotent processing.
            self._vector_store_repo.delete_vectors_in_document(
                item.namespace, item.doc_id
            )

            self._vector_store_repo.insert_vectors(
                namespace=item.namespace,
                document=item.doc_id,
                vectors=doc_embeddings,
                metadatas=list(
                    map(lambda d: {"content": d.text, **d.metadata}, doc_results)
                ),
            )
            process_status = DocumentProcessStatusEnum.Processed

        except Exception as e:
            cprint_cyan(f"process_vectors doc_id={item.doc_id} ERR >>> {e}")
            process_status = DocumentProcessStatusEnum.Error

        finally:
            DocumentDB.update(
                {
                    DocumentDB.process_status: process_status.value,
                    DocumentDB.summary: summary_all,
                    DocumentDB.embeddings: embeddings if len(embeddings) > 0 else None,
                }
            ).where(DocumentDB.doc_id == doc_id).execute()

    def delete_document(self, doc: Document):
        self._storage_facade.delete(doc.doc_id)
        self._vector_store_repo.delete_vectors_in_document(doc.namespace, doc.doc_id)
        DocumentDB.delete().where(DocumentDB.doc_id == doc.doc_id).execute()

    def set_visibility(self, document: Document, visibility: DocumentVisibilityEnum):
        document.to_db().update(
            {
                DocumentDB.visibility: visibility.value,
            }
        ).execute()

    def list_document_by_user(self, user_id: str, skip: int, limit: int):
        items = (
            DocumentDB.select()
            .where(DocumentDB.upload_by == user_id)
            .order_by(DocumentDB.upload_at)
            .paginate(skip, limit)
        )
        return [Document.from_db(i) for i in items]

    def list_document_public(self, skip: int, limit: int):
        items = (
            DocumentDB.select()
            .where(DocumentDB.visibility == DocumentVisibilityEnum.Public.value)
            .order_by(DocumentDB.upload_at)
            .paginate(skip, limit)
        )
        return [Document.from_db(i) for i in items]

    def get_document_vectors(self, doc_id: str):
        item = self.get_doc_or_not_found(doc_id)
        vectors = self._vector_store_repo.get_document_vectors(
            item.namespace, item.doc_id
        )
        return vectors

    def query_document_summary(
        self, namespace: str, query: str, user_id: str | None = None, limit: int = 5
    ):
        query_vector = self._llm.line_embeddings(query)

        # cosine distant. Ref: https://github.com/pgvector/pgvector
        _distant_search_method = "<=>"

        query_str = f"""
        SELECT 
            namespace,
            doc_id,
            filename,
            content_type,
            bytesize,
            upload_by,
            upload_at,
            summary,
            process_status,
            visibility,
            1 - (embeddings {_distant_search_method} %s::vector) AS similarity
        FROM documentdb
        WHERE namespace = %s """
        query_args = (query_vector, namespace)

        if user_id is not None:
            query_str += " AND upload_by = %s"
            query_args += (user_id,)
        else:
            query_str += " AND visibility = 'public'"

        query_str += " ORDER BY similarity DESC LIMIT %s"
        query_args += (limit,)

        results = self._execute(query_str, query_args) or []

        return [
            {
                "namespace": namespace,
                "doc_id": doc_id,
                "filename": filename,
                "content_type": content_type,
                "bytesize": bytesize,
                "upload_by": upload_by,
                "upload_at": upload_at,
                "summary": summary,
                "process_status": process_status,
                "visibility": visibility,
                "similarity": similarity,
            }
            for (
                namespace,
                doc_id,
                filename,
                content_type,
                bytesize,
                upload_by,
                upload_at,
                summary,
                process_status,
                visibility,
                similarity,
            ) in results
        ]

    def check_support_content_type(self, content_type: str):
        return self._document_parser.check_support_content_type(content_type)

    def get_support_content_type(self):
        return self._document_parser._support_types


# Create table if not exists
get_db().create_tables([DocumentDB])
