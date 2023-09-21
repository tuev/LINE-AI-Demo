import json
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel

from repository.helpers import make_chunks
from repository.db_connect_base import DbConnectBase


class VectorQueryResult(BaseModel):
    namespace: str
    document: str
    metadata: dict
    similarity: float


class Vector(BaseModel):
    namespace: str
    document: str
    vector_id: str
    metadata: dict


class VectorStoreRepo(DbConnectBase):
    def __init__(
        self,
        table_name: str,
        vector_size: int,
    ):
        self._TABLE_NAME = table_name
        self._VECTOR_SIZE = vector_size
        self._create_table()

    def _create_table(self):
        self._execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self._TABLE_NAME} (
                namespace VARCHAR(255),
                document VARCHAR(255),
                vector_id VARCHAR(255),
                metadata TEXT,
                vector vector({self._VECTOR_SIZE}),
                status VARCHAR(20)
            )""",
        )

    def _drop_table(self):
        self._execute(
            f"""
            DROP TABLE {self._TABLE_NAME}
            """
        )

    def delete_vectors_in_document(self, namespace: str, document: str = ""):
        # TODO: this does not yet handle multiple consecutive DELETEs

        query_str = f"DELETE FROM {self._TABLE_NAME} WHERE namespace = %s"

        query_args = (namespace,)
        if document != "":
            query_str += " AND document = %s"
            query_args += (document,)

        self._execute(query_str, query_args)

    def set_vector_status_by_ids(self, vector_ids: list[str], status: str):
        # TODO: this does not yet handle multiple consecutive UPDATEs
        query_str = ""
        query_args = ()
        for vector_id in vector_ids:
            query_str += f"""
                UPDATE {self._TABLE_NAME}
                SET status = '{status}'
                WHERE vector_id = %s;
                """
            query_args += (vector_id,)

        self._execute(query_str, query_args)

    def insert_vectors(
        self,
        namespace: str,
        document: str,
        vectors: list[list[float]],
        metadatas: list[dict],
        vector_ids: Optional[list[str]] = None,
    ):
        if len(vectors) != len(metadatas):
            raise Exception("len(vectors) must match len(metadata)")

        if vector_ids is not None and len(vector_ids) != len(vectors):
            raise Exception("len(vector_ids) must match len(vectors)")

        _metadatas: list[str] = []
        for m in metadatas:
            metadata_str = json.dumps(m)
            if len(metadata_str) > 40000:
                raise Exception("metadata greater than 40kb")

            _metadatas.append(metadata_str)

        _vector_ids: list[str] = (
            vector_ids if vector_ids is not None else [str(uuid4()) for _ in vectors]
        )
        vectors_and_metadata = list(zip(_vector_ids, vectors, _metadatas))
        vectors_and_metadata_len = len(vectors_and_metadata)
        inserted = 0
        _CHUNK_SIZE = 20
        for chunk in make_chunks(vectors_and_metadata, _CHUNK_SIZE):
            query_str = ""
            query_args = ()
            for vector_id, vector, metadata in chunk:
                query_str += f"""
                    INSERT INTO {self._TABLE_NAME}
                        (namespace, document, vector_id, vector, metadata, status)
                    VALUES (%s, %s, %s, %s, %s, 'active');
                    """
                query_args += (
                    namespace,
                    document,
                    vector_id,
                    vector,
                    metadata,
                )

            self._execute(query_str, query_args)

            inserted += len(chunk)
            print(f">>> inserted {inserted} / {vectors_and_metadata_len}")

        return _vector_ids

    def get_document_vectors(self, namespace: str, document: str = ""):
        query_str = f"""
        SELECT
            namespace,
            document,
            vector_id,
            metadata
        FROM {self._TABLE_NAME}
        WHERE namespace = %s
        """
        query_args = (namespace,)

        if document != "":
            query_str += " AND document = %s"
            query_args += (document,)

        results = self._execute(query_str, query_args) or []
        return [
            Vector(
                namespace=namespace,
                document=document,
                vector_id=vector_id,
                metadata=json.loads(metadata),
            )
            for (namespace, document, vector_id, metadata) in results
        ]

    def similarity_search_by_namespace(
        self,
        query_vector: list[float],
        namespace: str,
        document: str = "",
        limit: int = 5,
    ):
        # cosine distant. Ref: https://github.com/pgvector/pgvector
        _distant_search_method = "<=>"

        query_str = f"""
        SELECT 
            namespace,
            document,
            vector_id,
            metadata,
            1 - (vector {_distant_search_method} %s::vector) AS similarity
        FROM {self._TABLE_NAME}
        WHERE NOT status = 'inactive' AND namespace = %s
        """

        query_args = (query_vector, namespace)
        if document != "":
            query_str += " AND document = %s"
            query_args += (document,)

        query_str += " ORDER BY similarity DESC LIMIT %s"
        query_args += (limit,)

        results = self._execute(query_str, query_args) or []

        return [
            VectorQueryResult(
                namespace=namespace,
                document=document,
                metadata=json.loads(metadata),
                similarity=similarity,
            )
            for (namespace, document, _, metadata, similarity) in results
        ]

    def similarity_search_by_documents(
        self,
        query_vector: list[float],
        documents: list[str],
        limit: int = 5,
    ):
        # cosine distant. Ref: https://github.com/pgvector/pgvector
        _distant_search_method = "<=>"

        query_str = f"""
        SELECT 
            namespace,
            document,
            vector_id,
            metadata,
            1 - (vector {_distant_search_method} %s::vector) AS similarity
        FROM {self._TABLE_NAME}
        WHERE NOT status = 'inactive' AND document = ANY(%s)
        ORDER BY similarity DESC LIMIT %s
        """

        query_args = (query_vector, documents, limit)

        results = self._execute(query_str, query_args) or []

        return [
            VectorQueryResult(
                namespace=namespace,
                document=document,
                metadata=json.loads(metadata),
                similarity=similarity,
            )
            for (namespace, document, _, metadata, similarity) in results
        ]
