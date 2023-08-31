import json
from typing import Any, Generator, Tuple
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


class LLMFacade:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

    @staticmethod
    def make_prompt_request_body(prompt: str):
        return json.dumps(
            {
                "stream": True,
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

    def completion(self, prompt: str) -> Generator[dict, Any, Tuple[str, LLMUsage]]:
        s = requests.Session()
        data = self.make_prompt_request_body(prompt)

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
                            usage = LLMUsage.parse_obj(value)
                            return content, usage
                        else:
                            content += value.get("content")
                            yield value
                    except Exception as e:
                        print("ERR processing", line)
                        raise e

        return "", LLMUsage()
