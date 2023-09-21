from typing import List
from pydantic import BaseModel


class DocumentReference(BaseModel):
    filename: str
    doc_id: str
    upload_by: str
    content_type: str
    pages: List[int]
    text: List[str]
