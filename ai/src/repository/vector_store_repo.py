import json
from typing import Callable
from uuid import uuid4

from peewee import PostgresqlDatabase
from pgvector.psycopg2 import register_vector

from repository.helpers import make_chunks


class VectorQueryResult:
    def __init__(self, namespace: str, document: str, metadata: str, similarity: float):
        self.namespace = namespace
        self.document = document
        self.metadata = metadata
        self.similarity = similarity

    def to_dict(self):
        return {
            "namespace": self.namespace,
            "document": self.document,
            "metadata": self.metadata,
            "similarity": self.similarity,
        }


class VectorStoreRepo:
    def __init__(
        self,
        get_db: Callable[[], PostgresqlDatabase],
        table_name: str,
        vector_size: int,
    ):
        self._TABLE_NAME = table_name
        self._VECTOR_SIZE = vector_size
        self.get_db = get_db
        self._conn = get_db()
        self.register_vector_plugin()
        self.create_table()

    _conn = None

    def register_vector_plugin(self):
        register_vector(self.get_db())

    def execute(self, sql, args=None):
        """Below is a wrapper for the normal psycopg2 execute
        to fix the issue when psycopg2 unable to handle connection
        disconnected by the server by timeout or other unknown causes:
        - First check the current connection success.
        - If not close it and open new connection.
        - Then proceed to execute the query.
        """
        try:
            if self._conn is None:
                raise Exception("Not yet have connection.")

            with self._conn.cursor() as cursor:
                # Atempt to connect
                cursor.execute("SELECT 1 + 1;")

        except Exception as e:
            if self._conn is not None:
                self._conn.close()

            self._conn = self.get_db()
            print("Reconnected db", e)
            pass

        with self._conn.cursor() as cursor:
            cursor.execute(sql, args)
            if cursor is not None and cursor.pgresult_ptr is not None:
                return cursor.fetchall()

    def create_table(self):
        self.execute(
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

    def drop_table(self):
        self.execute(
            f"""
            DROP TABLE {self._TABLE_NAME}
            """
        )

    def delete_vectors_in_document(
        self, namespace: str, document: str = "", permanent: bool = False
    ):
        # TODO: this not yet handle too many DELETE

        if permanent:
            query_str = f"DELETE FROM {self._TABLE_NAME}"
        else:
            query_str = f"UPDATE {self._TABLE_NAME} SET status = 'inactive'"

        query_str += " WHERE namespace = %s"

        query_args = (namespace,)
        if document != "":
            query_str += " AND document = %s"
            query_args += (document,)

        self.execute(query_str, query_args)

    def set_vector_status_by_ids(self, vector_ids: list[str], status: str):
        # TODO: this not yet handle too many UPDATE
        query_str = ""
        query_args = ()
        for vector_id in vector_ids:
            query_str += f"""
                UPDATE {self._TABLE_NAME}
                SET status = '{status}'
                WHERE vector_id = %s;
                """
            query_args += (vector_id,)

        self.execute(query_str, query_args)

    def insert_vectors(
        self,
        namespace: str,
        document: str,
        vectors: list[list[float]],
        metadatas: list[dict],
    ):
        if len(vectors) != len(metadatas):
            raise Exception("len(vectors) must match len(metadata)")

        _metadatas: list[str] = []
        for m in metadatas:
            metadata_str = json.dumps(m)
            if len(metadata_str) > 40000:
                raise Exception("metadata greater than 40kb")

            _metadatas.append(metadata_str)

        vector_ids: list[str] = []
        vectors_and_metadata = list(zip(vectors, _metadatas))
        vectors_and_metadata_len = len(vectors_and_metadata)
        inserted = 0
        _CHUNK_SIZE = 20
        for chunk in make_chunks(vectors_and_metadata, _CHUNK_SIZE):
            query_str = ""
            query_args = ()
            for vector, metadata in chunk:
                vector_id = str(uuid4())
                vector_ids.append(vector_id)
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

            self.execute(query_str, query_args)

            inserted += len(chunk)
            print(f">>> inserted {inserted} / {vectors_and_metadata_len}")

        return vector_ids

    def get_document_vectors(self, namespace: str, document: str = ""):
        query_str = f"""
        SELECT vector_id FROM {self._TABLE_NAME}
        WHERE NOT status = 'inactive' AND namespace = %s
        """
        query_args = (namespace,)

        if document != "":
            query_str += " AND document = %s"
            query_args += (document,)

        results = self.execute(query_str, query_args) or []
        return [vector_id for (vector_id,) in results]

    def similarity_search(
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

        results = self.execute(query_str, query_args) or []

        return [
            VectorQueryResult(namespace, document, metadata, similarity)
            for (namespace, document, _, metadata, similarity) in results
        ]
