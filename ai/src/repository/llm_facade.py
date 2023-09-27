from enum import Enum
from typing import List

import requests
from fastapi import status
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import BaseMessage


class ChatModelEnum(str, Enum):
    Chat_3_5 = "gpt-3.5-turbo"
    Chat_4 = "gpt-4"

    def get_name(self):
        if self == self.Chat_3_5:
            return "GPT-3.5"

        if self == self.Chat_4:
            return "GPT-4"


class LLMFacade:
    def __init__(self, openai_key: str) -> None:
        self._embeddings = OpenAIEmbeddings(openai_api_key=openai_key)

    def _make_line_internal_chat_request(
        self,
        messages: List[BaseMessage],
        model: ChatModelEnum,
        cookie: str,
        stream: bool,
    ):
        url = "https://chatgpt.linecorp.com/api/chat"

        _system_prompt = ""
        _messages = []
        for m in messages:
            if m.type == "system":
                _system_prompt = m.content
            if m.type == "ai":
                _messages.append({"role": "assistant", "content": m.content})
            if m.type == "human":
                _messages.append({"role": "user", "content": m.content})

        payload = {
            "model": {
                "id": model,
                "name": model.get_name(),
            },
            "messages": _messages,
            "key": "",
            "prompt": _system_prompt,
            "temperature": 0.1,
        }

        headers = {"Cookie": f"_inhouse_chatgpt={cookie}"}
        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            stream=stream,
            timeout=120,  # TODO: Move timeout to env
        )

        return resp

    def internal_chat(
        self,
        messages: List[BaseMessage],
        model: ChatModelEnum,
        internal_token: str,
    ):
        resp = self._make_line_internal_chat_request(
            messages,
            model,
            internal_token,
            stream=False,
        )
        return resp.text

    def openai_embeddings(self, text: str) -> List[float]:
        return self._embeddings.embed_query(text)

    def healthcheck_line_embedding(self) -> bool:
        resp = requests.get(
            "http://jp.deeppocket.linecorp.com/contents-ml/embtxt-mling-xlm-xl-pca/monitor/l7check"
        )
        return resp.status_code == status.HTTP_200_OK

    def line_embeddings(self, text: str) -> List[float]:
        res = requests.post(
            "http://jp.deeppocket.linecorp.com/contents-ml/embtxt-mling-xlm-xl-pca/get_emb",
            json={"text": text, "normalize": True, "startidx": 0},
            timeout=10,
        )
        data = res.json()
        if data.get("status") != "SUCCESS":
            print("embbedings ERR >>>", res.text)
            raise Exception("erro getting embeddings")

        return data.get("emb", [])
