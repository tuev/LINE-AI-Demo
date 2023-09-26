import re
from typing import Any, List
import trafilatura

import requests
from pydantic import BaseModel


class DocumentParseResult(BaseModel):
    text: str
    metadata: dict


class DocumentParser:
    def __init__(self, unstructured_endpoint: str, support_types: str):
        self._unstructured_endpoint = unstructured_endpoint
        self._support_types = support_types.split(",")
        pass

    def check_support_content_type(self, content_type: str):
        return content_type in self._support_types

    def call_unstructured_api(
        self, document_id: str, file_bytes: bytes, content_type: str
    ) -> List[Any]:
        _content_type = content_type.split(";")[0]
        url = self._unstructured_endpoint + "/general/v0/general"
        r = requests.post(
            url,
            files={"files": (document_id, file_bytes, _content_type)},
        )
        try:
            return r.json()
        except Exception as e:
            print("Error from Unstructured", e)
            print(r.text)
            raise e

    def html_to_text(self, html: str):
        return trafilatura.extract(html)

    def simple_parse(
        self, unstructured_docs: List[dict], split_length
    ) -> List[DocumentParseResult]:
        docs: List[DocumentParseResult] = []
        for d in unstructured_docs:
            content = d.get("text", "")

            content = content.replace("\t", " ")
            content = re.sub(
                r"^(?:[\t ]*(?:\r?\n|\r))+", "\\n", content, 0, re.MULTILINE
            )
            content = re.sub(r"\s\s*", " ", content, 0, re.MULTILINE)
            metadata = d.get("metadata", {})
            page_number = metadata.get("page_number", 0)
            metadata = {"page_number": int(page_number)}

            # First element
            if len(docs) == 0:
                docs.append(
                    DocumentParseResult(text=content or "", metadata=metadata or {})
                )
                continue

            # Handling next doc condition
            last_page = docs[-1]
            if len(last_page.text) > split_length:
                # Add overlap
                overlap_words_amount = 100
                previous_text = ""
                if len(docs) > 2:
                    previous_text = " ".join(
                        docs[-2].text.split()[-overlap_words_amount:]
                    )
                next_text = " ".join(content.split()[:overlap_words_amount])
                docs[-1].text = (
                    previous_text + "\n\n" + last_page.text + "\n\n" + next_text
                )

                # Add new chunk
                docs.append(DocumentParseResult(text=content, metadata=metadata))

                continue

            # Just add content to text
            docs[-1].text += "\n\n" + content

        # Handle when last doc has small length, We will add it to the previous doc
        if len(docs) > 2 and len(docs[-1].text) < split_length / 2:
            docs[-2].text += docs[-1].text
            docs = docs[:-2]

        return docs
