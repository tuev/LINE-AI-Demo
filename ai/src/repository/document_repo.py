import json
import multiprocessing
import traceback
from datetime import datetime
from enum import Enum
from typing import BinaryIO, List, Tuple
from uuid import uuid4

import numpy as np
import yaml
from fastapi import HTTPException, status
from peewee import CharField, DateTimeField, IntegerField, TextField
from pydantic import BaseModel
from sklearn.cluster import KMeans
from systems.base_ai_ystem import BaseAISystem

from repository.base_db import (
    BaseDBModel,
    VectorField,
    from_datetime,
    from_int,
    from_str,
    get_db,
)
from repository.db_connect_base import DbConnectBase
from repository.document_parser import DocumentParser
from repository.helpers import cprint_cyan, cprint_green, get_timestamp, messages_to_str
from repository.llm_facade import ChatModelEnum, LLMFacade
from repository.storage_facade import StorageFacade
from repository.vector_store_repo import VectorMetadata, VectorStoreRepo


class DocumentDB(BaseDBModel):
    namespace = CharField()
    doc_id = CharField(unique=True)
    filename = CharField()
    content_type = CharField()
    bytesize = IntegerField()  # NOTE: IntegerField limit is 2147483648 ~ 2GB
    upload_by = CharField()
    upload_at = DateTimeField()
    summary = TextField()
    summary_vector = VectorField(length=1536, null=True)
    process_status = CharField()
    visibility = CharField()
    metadata = TextField()


class DocumentProcessStatusEnum(Enum):
    Uploaded = "upload"
    Processing = "processing"
    Error = "error"
    Processed = "processed"


class DocumentVisibilityEnum(Enum):
    Public = "public"
    Private = "private"
    Link = "link"


class DocumentSourceTypeEnum(Enum):
    UploadFile = "upload-file"
    Landpress = "landpress"
    UploadText = "upload-text"


class DocumentMetadata(BaseModel):
    source_type: DocumentSourceTypeEnum
    source_link: str
    source_metadata: dict


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
    metadata: DocumentMetadata

    def to_db(self) -> DocumentDB:
        if self.metadata is None:
            metadata = None
        else:
            metadata = self.metadata.json()

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
            metadata=metadata,
        )

    @staticmethod
    def from_db(db_document: DocumentDB):
        return Document(
            namespace=from_str(db_document.namespace),
            doc_id=from_str(db_document.doc_id),
            filename=from_str(db_document.filename),
            content_type=from_str(db_document.content_type),
            bytesize=from_int(db_document.bytesize),
            upload_by=from_str(db_document.upload_by),
            upload_at=from_datetime(db_document.upload_at),
            summary=from_str(db_document.summary),
            process_status=DocumentProcessStatusEnum(db_document.process_status),
            visibility=DocumentVisibilityEnum(db_document.visibility),
            metadata=DocumentMetadata.parse_obj(
                json.loads(from_str(db_document.metadata))
            ),
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

        self._summary_prompt = BaseAISystem.load_messages(config, "Summary")
        self._summary_all_prompt = BaseAISystem.load_messages(config, "SummaryAll")

    def get_doc_or_not_found(self, id: str) -> Document:
        item = DocumentDB.get_or_none(DocumentDB.doc_id == id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="not found document"
            )

        return item

    def get_docs_or_raise_not_found(self, ids: List[str]) -> List[Document]:
        items = DocumentDB.select().where(DocumentDB.doc_id.in_(ids))
        if len(items) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="not found document"
            )

        return [Document.from_db(i) for i in items]

    def create(
        self,
        namespace: str,
        filename: str,
        upload_by: str,
        content_type: str,
        blob: BinaryIO,
        bytesize: int,
        visibility: DocumentVisibilityEnum,
        metadata: DocumentMetadata,
    ):
        doc_id = str(uuid4())
        self._storage_facade.upload(
            object_name=doc_id,
            content_type=content_type,
            part_size=self.MAX_PART_SIZE,
            blob=blob,
            metadata=None,
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
            metadata=metadata,
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
                pool.apply_async(self._llm.openai_embeddings, (doc,))
                for doc in doc_results
            ]
            for result in workers:
                doc_embeddings.append(result.get())

        return doc_embeddings

    def _get_document_cluster_for_summary(
        self, doc_embeddings: List[List[float]], num_clusters: int = 5
    ):
        _num_clusters = min(len(doc_embeddings), num_clusters)
        kmeans = KMeans(n_clusters=_num_clusters, random_state=42, n_init="auto").fit(
            doc_embeddings
        )
        closest_indices = get_closest_indices(doc_embeddings, _num_clusters, kmeans)
        closest_indices = sorted(closest_indices)
        return closest_indices

    def _get_summary_of_text(self, text: str):
        messages = self._summary_prompt.format_prompt(text=text).to_messages()
        cprint_cyan(messages_to_str(messages))
        chat = self._llm.create_chat(model=ChatModelEnum.Chat_3_5, temperature=0.1)
        summary = chat(messages=messages).content
        cprint_green(">" * 80)
        cprint_green(summary)
        cprint_green("=" * 80)

        return summary

    def _get_combined_summary(self, texts: List[str]):
        combined_summary_list = "\n---\n".join(texts)
        messages = self._summary_all_prompt.format_prompt(
            text=combined_summary_list
        ).to_messages()
        cprint_cyan(messages_to_str(messages))
        chat = self._llm.create_chat(model=ChatModelEnum.Chat_3_5, temperature=0.1)
        summary_all = chat(messages=messages).content
        cprint_cyan(summary_all)

        return summary_all

    def summary_texts(self, texts: List[str]) -> Tuple[str, List[float]]:
        summaries: List[str] = []
        for text in texts:
            summary = self._get_summary_of_text(text)
            summaries.append(summary)

        summary_all = self._get_combined_summary(summaries)
        summary_vector = self._llm.openai_embeddings(summary_all)

        return summary_all, summary_vector

    def process_vector_and_summary(self, doc_id: str):
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
        summary_vector: List[float] = []

        try:
            if item.content_type in ["text/markdown", "text/plain"]:
                unstructured_docs = [
                    {"text": t} for t in data.decode("utf-8").split("\n")
                ]
                doc_results = self._document_parser.simple_parse(
                    unstructured_docs, split_length=2000
                )
            else:
                unstructured_docs = self._document_parser.call_unstructured_api(
                    document_id=item.doc_id,
                    file_bytes=data,
                    content_type=item.content_type,
                )
                doc_results = self._document_parser.simple_parse(
                    unstructured_docs, split_length=2000
                )

            doc_embeddings = self._get_document_embbedings(
                list(map(lambda d: d.text, doc_results))
            )

            cluster_indices = self._get_document_cluster_for_summary(doc_embeddings)

            summary_all, summary_vector = self.summary_texts(
                [doc_results[i].text for i in cluster_indices]
            )

            # Clean up existing vectors for idempotent processing.
            self._vector_store_repo.delete_vectors_in_document(
                item.namespace, item.doc_id
            )

            self._vector_store_repo.insert_vectors(
                namespace=item.namespace,
                document=item.doc_id,
                vectors=doc_embeddings,
                metadatas=list(
                    map(
                        lambda d: VectorMetadata(
                            content=d.text,
                            page_number=d.metadata.get("page_number", 0),
                        ),
                        doc_results,
                    )
                ),
            )
            process_status = DocumentProcessStatusEnum.Processed

        except Exception as e:
            print(traceback.format_exc())
            cprint_cyan(f"process_vectors doc_id={item.doc_id} ERR >>> {e}")
            process_status = DocumentProcessStatusEnum.Error

        finally:
            DocumentDB.update(
                {
                    DocumentDB.process_status: process_status.value,
                    DocumentDB.summary: summary_all,
                    DocumentDB.summary_vector: summary_vector
                    if len(summary_vector) > 0
                    else None,
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
        query_vector = self._llm.openai_embeddings(query)

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
            1 - (summary_vector {_distant_search_method} %s::vector) AS similarity
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
