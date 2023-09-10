import os
import tempfile
from typing import Annotated, List
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from pydantic import BaseModel


from repository import document_repo, auth_repo
from repository.auth_repo import LineUserInfo
from repository.document_repo import DocumentVisibilityEnum

document_router = APIRouter(prefix="/document")


class PostLearnJapaneseTranslate(BaseModel):
    sentences: List[str]


class UploadDocument(BaseModel):
    file: str


@document_router.post("/upload")
def upload(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    file: Annotated[
        UploadFile,
        File(
            description=f"The file must be smaller than {document_repo.MAX_SIZE_TEXT}."
        ),
    ],
    namespace: Annotated[
        str,
        Form(description="Namespace of the file. Example: /my-org/human-resource"),
    ],
    visibility: Annotated[
        DocumentVisibilityEnum, Form(description="Metadata for file")
    ],
    background_task: BackgroundTasks,
):
    filename = file.filename
    content_type = file.content_type
    bytesize = file.size

    def missing_file_detail(field: str):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"missing {field}"
        )

    if filename is None:
        raise missing_file_detail("filename")

    if content_type is None:
        raise missing_file_detail("content_type")

    if bytesize is None:
        raise missing_file_detail("bytesize")

    if bytesize > document_repo.MAX_PART_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The file must be smaller than {document_repo.MAX_SIZE_TEXT}.",
        )

    internal_token = auth_repo.get_token(user.sub)
    if internal_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="internal token not found",
        )

    if internal_token.is_expired():
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="unable to proceed because the internal token is about to expire.",
        )

    doc_id = document_repo.create(
        namespace=namespace,
        filename=filename,
        content_type=content_type,
        blob=file.file,
        bytesize=file.size or -1,
        upload_by=user.sub,
        visibility=visibility,
    )

    background_task.add_task(
        document_repo.process_vector_and_summary,
        internal_token=internal_token.token,
        doc_id=doc_id,
    )

    return doc_id


def remove_temp_file(path: str):
    os.remove(path)


@document_router.get("/get_object/{document_id}")
def get_object(document_id: str, background_task: BackgroundTasks):
    doc, blob = document_repo.get_object(doc_id=document_id)
    if doc is None or blob is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="notfound")

    temp_file = tempfile.NamedTemporaryFile(delete=False)

    with open(temp_file.name, "wb") as f:
        f.write(blob)

    resp = FileResponse(
        path=temp_file.name,
        filename=doc.filename,
        headers={"Content-Disposition": "inline"},
    )

    background_task.add_task(remove_temp_file, temp_file.name)

    return resp


@document_router.post("/do_process/{document_id}")
def do_process(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    document_id: str,
):
    internal_token = auth_repo.get_token(user.sub)

    if internal_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="internal token not found",
        )

    if internal_token.is_expired():
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="unable to proceed because the internal token is about to expire.",
        )

    document_repo.process_vector_and_summary(internal_token.token, document_id)
    return "success"


@document_router.delete("/delete/{document_id}")
def delete(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    document_id: str,
):
    doc = document_repo.get(document_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="not found document"
        )

    if doc.upload_by != user.sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user is not owner of this document",
        )

    document_repo.delete_document(doc)
    return "success"


@document_router.get("/vectors/{document_id}")
def vectors(document_id: str):
    vectors = document_repo.get_document_vectors(document_id)
    return vectors


@document_router.get("/list_my")
def list_my(user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)]):
    docs = document_repo.list_document_by_user(user.sub)
    return docs


@document_router.put("/set_visibility/{document_id}/{visibility}")
def set_visibility(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    document_id: str,
    visibility: DocumentVisibilityEnum,
):
    doc = document_repo.get(document_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="not found document"
        )

    if doc.upload_by != user.sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user is not owner of this document",
        )

    document_repo.set_visibility(doc, visibility)

    return "success"


@document_router.get("/list_public")
def list_public():
    docs = document_repo.list_document_public()
    return docs


class QueryMyDocumentSummary(BaseModel):
    namespace: str
    query: str
    limit: int = 5


@document_router.post("/query_my_document_summary")
def query_my_document_summary(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    body: QueryMyDocumentSummary,
):
    results = document_repo.query_document_summary(
        namespace=body.namespace,
        query=body.query,
        limit=body.limit,
        user_id=user.sub,
    )
    return results


class queryPublicDocumentSummary(BaseModel):
    namespace: str
    query: str
    limit: int = 5


@document_router.post("/query_public_document_summary")
def query_public_document_summary(
    body: queryPublicDocumentSummary,
):
    results = document_repo.query_document_summary(
        namespace=body.namespace,
        query=body.query,
        limit=body.limit,
    )
    return results
