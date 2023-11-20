import io
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
from repository import auth_repo, document_download, document_parser, document_repo
from repository.auth_repo import LineUserInfo
from repository.document_repo import (
    DocumentMetadata,
    DocumentSourceTypeEnum,
    DocumentVisibilityEnum,
)

document_router = APIRouter(prefix="/document")


class PostLearnJapaneseTranslate(BaseModel):
    sentences: List[str]


class UploadDocument(BaseModel):
    file: str


@document_router.post("/upload/file")
def upload_file(
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
    background_tasks: BackgroundTasks,
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

    if document_repo.check_support_content_type(content_type) is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content_type. Support: {document_repo.get_support_content_type()}",
        )

    if bytesize is None:
        raise missing_file_detail("bytesize")

    if bytesize > document_repo.MAX_PART_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The file must be smaller than {document_repo.MAX_SIZE_TEXT}.",
        )

    doc_id = document_repo.create(
        namespace=namespace,
        filename=filename,
        content_type=content_type,
        blob=file.file,
        bytesize=file.size or -1,
        upload_by=user.sub,
        visibility=visibility,
        metadata=DocumentMetadata(
            source_type=DocumentSourceTypeEnum.UploadFile,
            source_link=filename,
            source_metadata={},
        ),
    )

    background_tasks.add_task(
        document_repo.process_vector_and_summary,
        doc_id=doc_id,
    )

    return doc_id


class UploadText(BaseModel):
    namespace: str
    title: str
    text: str
    visibility: DocumentVisibilityEnum


@document_router.post("/upload/text")
def upload_text(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    body: UploadText,
    background_tasks: BackgroundTasks,
):
    if len(body.text) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="must have title"
        )

    min_body = 300

    if len(body.text) < min_body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"body is too small. must have more than {min_body} characters",
        )

    text_encode = body.text.encode(encoding="utf-8")

    doc_id = document_repo.create(
        namespace=body.namespace,
        filename=body.title,
        content_type="text/plain",
        blob=io.BytesIO(text_encode),
        bytesize=len(text_encode),
        upload_by=user.sub,
        visibility=body.visibility,
        metadata=DocumentMetadata(
            source_type=DocumentSourceTypeEnum.UploadText,
            source_link="",
            source_metadata={},
        ),
    )

    background_tasks.add_task(
        document_repo.process_vector_and_summary,
        doc_id=doc_id,
    )

    return doc_id


class UploadLandpress(BaseModel):
    namespace: str
    visibility: DocumentVisibilityEnum
    url: str


@document_router.post("/upload/landpress")
def upload_landpress(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    body: UploadLandpress,
    background_tasks: BackgroundTasks,
):
    doc = document_download.landpress_or_none(body.url)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    min_body = 300

    if len(doc.body) < min_body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"body is too small. must have more than {min_body} characters",
        )

    text_encode = doc.body.encode(encoding="utf-8")

    doc_id = document_repo.create(
        namespace=body.namespace,
        filename=doc.title,
        content_type="text/markdown",
        blob=io.BytesIO(text_encode),
        bytesize=len(text_encode),
        upload_by=user.sub,
        visibility=body.visibility,
        metadata=DocumentMetadata(
            source_type=DocumentSourceTypeEnum.Landpress,
            source_link=body.url,
            source_metadata=dict(
                create_by=doc.create_by,
                create_at=doc.create_at,
                update_at=doc.update_at,
            ),
        ),
    )

    background_tasks.add_task(
        document_repo.process_vector_and_summary,
        doc_id=doc_id,
    )

    return doc_id


class ParseHtmlPage(BaseModel):
    html: str


@document_router.post("/parse/html_page")
def parse_html_page(
    _: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    body: ParseHtmlPage,
):
    text = document_parser.html_to_text(body.html)
    return text


def remove_temp_file(path: str):
    os.remove(path)


@document_router.get("/get_object/{document_id}")
def get_object(document_id: str, background_tasks: BackgroundTasks):
    doc = document_repo.get_doc_or_not_found(document_id)
    blob = document_repo.get_file_or_not_found(document_id)

    temp_file = tempfile.NamedTemporaryFile(delete=False)

    with open(temp_file.name, "wb") as f:
        f.write(blob)

    resp = FileResponse(
        path=temp_file.name,
        filename=doc.filename,
        headers={"Content-Disposition": "inline"},
    )

    background_tasks.add_task(remove_temp_file, temp_file.name)

    return resp


@document_router.post("/do_process/{doc_id}")
def do_process(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    doc_id: str,
    background_tasks: BackgroundTasks,
):
    background_tasks.add_task(
        document_repo.process_vector_and_summary,
        doc_id=doc_id,
    )

    return "success"


@document_router.delete("/delete/{document_id}")
def delete(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    document_id: str,
):
    doc = document_repo.get_doc_or_not_found(document_id)

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


@document_router.put("/set_visibility/{document_id}/{visibility}")
def set_visibility(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    document_id: str,
    visibility: DocumentVisibilityEnum,
):
    doc = document_repo.get_doc_or_not_found(document_id)

    if doc.upload_by != user.sub:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user is not owner of this document",
        )

    document_repo.set_visibility(doc, visibility)

    return "success"


@document_router.get("/list_my/")
def list_my(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    skip: int = 0,
    limit: int = 10,
):
    docs = document_repo.list_document_by_user(user.sub, skip, limit)
    return docs


@document_router.get("/list_public/")
def list_public(
    user: Annotated[LineUserInfo, Depends(auth_repo.get_current_user)],
    skip: int = 0,
    limit: int = 10,
):
    docs = document_repo.list_document_public(skip, limit)
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


class QueryPublicDocumentSummary(BaseModel):
    namespace: str
    query: str
    limit: int = 5


@document_router.post("/query_public_document_summary")
def query_public_document_summary(
    body: QueryPublicDocumentSummary,
):
    results = document_repo.query_document_summary(
        namespace=body.namespace,
        query=body.query,
        limit=body.limit,
    )
    return results
