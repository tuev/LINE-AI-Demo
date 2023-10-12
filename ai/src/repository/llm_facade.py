from enum import Enum
from typing import List

from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI


class ChatModelEnum(str, Enum):
    Chat_3_5 = "gpt-3.5-turbo"
    Chat_4 = "gpt-4"


class LLMFacade:
    def __init__(self, openai_key: str) -> None:
        self._embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
        self._openai_key = openai_key

    def create_chat(self, model: ChatModelEnum, temperature: float) -> ChatOpenAI:
        return ChatOpenAI(
            temperature=temperature,
            openai_api_key=self._openai_key,
            model=model,
        )

    def openai_embeddings(self, text: str) -> List[float]:
        return self._embeddings.embed_query(text)
