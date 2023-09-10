from typing import BinaryIO
from minio import Minio


class StorageFacade:
    def __init__(self, client: Minio, bucket_name: str) -> None:
        self._client = client
        self._bucket_name = bucket_name

    def upload(
        self,
        object_name: str,
        content_type: str,
        blob: BinaryIO,
        part_size: int,
        metadata: dict | None = None,
    ):
        # TODO: Move to configuration

        return self._client.put_object(
            bucket_name=self._bucket_name,
            object_name=object_name,
            data=blob,
            length=-1,
            part_size=part_size,
            content_type=content_type,
            metadata=metadata,
        )

    def get(self, object_name: str) -> bytes | None:
        response = None
        try:
            response = self._client.get_object(
                bucket_name=self._bucket_name,
                object_name=object_name,
            )
            data = response.read()
            return data

        except Exception as e:
            return None

        finally:
            if response is not None:
                response.close()
                response.release_conn()

    def delete(self, object_name: str):
        self._client.remove_object(
            bucket_name=self._bucket_name,
            object_name=object_name,
        )
