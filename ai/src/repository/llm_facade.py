import json
from typing import Any, Generator
from pydantic import BaseModel

import requests


class LLMTimings(BaseModel):
    predicted_ms: float = 0.0
    predicted_n: int = 0
    predicted_per_second: float = 0.0
    predicted_per_token_ms: float = 0.0
    prompt_ms: float = 0.0
    prompt_n: int = 0
    prompt_per_second: float = 0.0
    prompt_per_token_ms: float = 0.0


class LLMUsage(BaseModel):
    timings: LLMTimings = LLMTimings()
    tokens_evaluated: int = 0
    tokens_predicted: int = 0


class LLMFinalContent(BaseModel):
    final_content: str
    usage: LLMUsage
    stop: bool


class LLMStreamContent(BaseModel):
    content: str
    stop: bool


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

        with s.post(f"{self.endpoint}/completion", data=data, stream=True) as resp:
            content = ""
            for line in resp.iter_lines():
                if line:
                    try:
                        data_str = line.decode("utf-8").split("data: ")[1]
                        value = json.loads(data_str)
                        if value.get("stop", True) is True:
                            value["timings"]["prompt_per_second"] = (
                                value["timings"]["prompt_per_second"] or 0.0
                            )
                            value["final_content"] = content
                            usage = LLMUsage.parse_obj(value)
                            final_content = LLMFinalContent(
                                final_content=content, usage=usage, stop=True
                            )
                            yield final_content
                        else:
                            llm_content = LLMStreamContent.parse_obj(value)
                            content += llm_content.content
                            yield llm_content

                    except Exception as e:
                        print("LLM completion ERR processing stream", line)
                        raise e
