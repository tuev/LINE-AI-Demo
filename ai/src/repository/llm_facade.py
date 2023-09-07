from enum import Enum
import json
from typing import Any, Generator, List, Optional
from fastapi import HTTPException, status
from langchain.schema import BaseMessage
from pydantic import BaseModel


import requests


class LLMTimings(BaseModel):
    predicted_ms: Optional[float]
    predicted_n: Optional[int]
    predicted_per_second: Optional[float]
    predicted_per_token_ms: Optional[float]
    prompt_ms: Optional[float]
    prompt_n: Optional[int]
    prompt_per_second: Optional[float]
    prompt_per_token_ms: Optional[float]


class LLMUsage(BaseModel):
    timings: LLMTimings
    tokens_evaluated: Optional[int]
    tokens_predicted: Optional[int]


class LLMFinalContent(BaseModel):
    stop: bool
    final_content: str
    usage: Optional[LLMUsage]
    err: Optional[str]


class LLMStreamContent(BaseModel):
    stop: bool
    content: str


class ChatModelEnum(str, Enum):
    Chat_3_5 = "gpt-3.5-turbo"
    Chat_4 = "gpt-4"

    def get_name(self):
        if self == self.Chat_3_5:
            return "GPT-3.5"

        if self == self.Chat_4:
            return "GPT-4"


class LLMFacade:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def _make_prompt_request_body(prompt: str):
        # TODO: Move these configuration to env
        return json.dumps(
            {
                "stream": True,  # Always streaming for now
                "n_predict": 500,
                "temperature": 0,
                "stop": ["</s>"],
                "repeat_last_n": 256,
                "repeat_penalty": 1.18,
                "top_k": 40,
                "top_p": 0.5,
                "tfs_z": 1,
                "typical_p": 1,
                "presence_penalty": 0,
                "frequency_penalty": 0,
                "mirostat": 0,
                "mirostat_tau": 5,
                "mirostat_eta": 0.1,
                "grammar": "",
                "n_probs": 0,
                "prompt": prompt,
            }
        )

    def _handle_stream_response(self, resp: requests.Response):
        content = ""
        try:
            for line in resp.iter_lines():
                if line:
                    try:
                        data_str = line.decode("utf-8").split("data: ")[1]
                        print(">>>", data_str)
                        value = json.loads(data_str)
                        if value.get("stop", True) is True:
                            value["final_content"] = content
                            usage = LLMUsage.parse_obj(value)
                            final_content = LLMFinalContent(
                                stop=True,
                                final_content=content,
                                usage=usage,
                                err=None,
                            )
                            yield final_content
                        else:
                            llm_content = LLMStreamContent.parse_obj(value)
                            content += llm_content.content
                            yield llm_content

                    except Exception as e:
                        print("LLM completion ERR processing stream", line)
                        raise e

        except requests.exceptions.Timeout:
            final_content = LLMFinalContent(
                stop=True,
                final_content=content,
                usage=None,
                err="timeout",
            )
            yield final_content

    def completion(
        self, prompt: str
    ) -> Generator[LLMFinalContent | LLMStreamContent, Any, None]:
        data = self._make_prompt_request_body(prompt)
        resp = requests.post(
            f"{self.endpoint}/completion",
            data=data,
            stream=True,
            timeout=60,  # TODO: Move timeout to env
        )
        return self._handle_stream_response(resp)

    def _handle_chunk_response(
        self, resp: requests.Response
    ) -> Generator[LLMFinalContent | LLMStreamContent, Any, None]:
        if resp.status_code != 200:
            print("internal_chat ERR >>", resp.text)
            raise Exception("error _handle_chunk_response")

        content = ""
        for chunk in resp.iter_content(chunk_size=128):
            content += chunk.decode("utf-8")
            yield LLMStreamContent(stop=False, content=chunk)

        yield LLMFinalContent(stop=True, final_content=content, usage=None, err=None)

        return None

    def _make_line_internal_chat_request(
        self,
        messages: List[BaseMessage],
        model: ChatModelEnum,
        cookie: str,
        max_length: int,
        token_limit: int,
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
                "maxLength": max_length,
                "tokenLimit": token_limit,
            },
            "messages": _messages,
            "key": "",
            "prompt": _system_prompt,
            "temperature": 0.5,
        }

        headers = {"Cookie": f"_inhouse_chatgpt={cookie}"}
        resp = requests.post(
            url,
            json=payload,
            headers=headers,
            stream=stream,
            timeout=60,  # TODO: Move timeout to env
        )

        return resp

    def internal_chat(
        self,
        messages: List[BaseMessage],
        model: ChatModelEnum,
        cookie: str,
        max_length: int = 12000,
        token_limit: int = 4000,
    ):
        resp = self._make_line_internal_chat_request(
            messages,
            model,
            cookie,
            max_length,
            token_limit,
            stream=True,
        )
        return resp.text

    def internal_chat_stream(
        self,
        messages: List[BaseMessage],
        model: ChatModelEnum,
        cookie: str,
        max_length: int = 12000,
        token_limit: int = 4000,
    ) -> Generator[LLMFinalContent | LLMStreamContent, Any, None]:
        resp = self._make_line_internal_chat_request(
            messages,
            model,
            cookie,
            max_length,
            token_limit,
            stream=True,
        )
        try:
            return self._handle_chunk_response(resp)
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="error from internal chat",
            )

    def healthcheck_embedding(self):
        resp = requests.get(
            "http://jp.deeppocket.linecorp.com/contents-ml/embtxt-mling-xlm-xl-pca/monitor/l7check"
        )
        return resp.status_code == status.HTTP_200_OK

    def embeddings(self, text: str) -> List[float]:
        res = requests.post(
            "http://jp.deeppocket.linecorp.com/contents-ml/embtxt-mling-xlm-xl-pca/get_emb",
            json={"text": text, "normalize": True, "startidx": 0},
        )
        data = res.json()
        if data.get("status") != "SUCCESS":
            print("embbedings ERR >>>", res.text)
            raise Exception("erro getting embeddings")

        return data.get("emb", [])
