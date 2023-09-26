from datetime import datetime
from pydantic import BaseModel
import requests


class DocumentDownloadResult(BaseModel):
    title: str
    body: str
    create_by: str
    create_at: datetime
    update_at: datetime


class DocumentDownload:
    def __init__(self) -> None:
        pass

    @staticmethod
    def landpress_or_none(url: str) -> DocumentDownloadResult | None:
        res = requests.get(url, timeout=10)
        data = res.json()

        if data.get("header", {}).get("success", False) is not True:
            status_code = data.get("header", {}).get("statusCode", None)
            if status_code == 404:
                return None

            else:
                raise Exception("DocumentDownload landpress failed", res.text)

        body = data["body"]
        return DocumentDownloadResult.parse_obj(
            dict(
                title=body.get("title", ""),
                body=body.get("body", ""),
                create_by=body.get("create_by", ""),
                create_at=body.get("createdAt", ""),
                update_at=body.get("updatedAt", ""),
            )
        )
