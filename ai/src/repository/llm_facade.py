import json
from typing import Any, Generator, Optional
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

    def completion(
        self, prompt: str
    ) -> Generator[LLMFinalContent | LLMStreamContent, Any, None]:
        s = requests.Session()
        data = self._make_prompt_request_body(prompt)

        with s.post(
            f"{self.endpoint}/completion",
            data=data,
            stream=True,
            timeout=60,  # TODO: Move timeout to env
        ) as resp:
            content = ""
            try:
                for line in resp.iter_lines():
                    if line:
                        try:
                            data_str = line.decode("utf-8").split("data: ")[1]
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
