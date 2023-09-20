from datetime import datetime
from typing import List, TypeVar
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from pydantic import BaseModel

import yaml
from repository.helpers import cprint_cyan, cprint_green, get_timestamp, messages_to_str
from repository.llm_facade import ChatModelEnum, LLMFacade
from repository.vector_store_repo import VectorQueryResult, VectorStoreRepo
from systems.base_ai_ystem import BaseAISystem

T = TypeVar("T")


class ExtractResult(BaseModel):
    question: str
    result: str
    references: List[VectorQueryResult]
    duration_ms: int
    timestamp: datetime


class SimpleAISystem:
    def __init__(self, llm: LLMFacade, vector_store_repo: VectorStoreRepo):
        self._llm = llm
        self._vector_store_repo = vector_store_repo

        with open("/app/src/prompts/simple.yaml") as f:
            config = yaml.safe_load(f)

        self._extract_prompt = BaseAISystem.load_messages_chat(config, "Extract")

    def extract(self, token: str, question: str, documents: List[str]) -> ExtractResult:
        start_ts = get_timestamp()
        query_vector = self._llm.line_embeddings(question)
        result_references = self._vector_store_repo.similarity_search_by_documents(
            query_vector, documents
        )

        do_llm_chat4 = BaseAISystem.do_llm_with_model(
            self._llm,
            token,
            ChatModelEnum.Chat_4,
        )

        messages = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(self._extract_prompt),
                HumanMessagePromptTemplate.from_template("""\
PARAGRAPHS

{paragraphs}

My question is: {question}
"""),
            ]
        )
        messages_prompt = messages.format_prompt(
            paragraphs="\n---\n".join(
                [r.metadata.get("content", "") for r in result_references]
            ),
            question=question,
        ).to_messages()
        planning_res = do_llm_chat4(messages_prompt)
        cprint_green(messages_to_str(messages_prompt))
        cprint_cyan(planning_res)
        cprint_cyan("-" * 80)

        end_ts = get_timestamp()

        return ExtractResult(
            question=question,
            result=planning_res,
            references=result_references,
            duration_ms=int((start_ts - end_ts).microseconds / 1000),
            timestamp=get_timestamp(),
        )
