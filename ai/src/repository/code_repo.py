import yaml

from repository.base_repo import BaseRepo
from repository.helpers import print_prompt
from repository.llm_facade import LLMFacade


class CodeRepo(BaseRepo):
    def __init__(self, llm: LLMFacade):
        self.llm = llm

        with open("./prompts/code.yaml") as f:
            config = yaml.safe_load(f)

        self._completion_prompt = self.load_messages(config, "Completion")

    def completion(self, query: str):
        prompt = self._completion_prompt.format(input=query)
        print_prompt(prompt)
        return self.llm.completion(prompt)
