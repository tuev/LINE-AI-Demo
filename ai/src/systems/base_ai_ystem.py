from typing import List
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMessage

from repository.llm_facade import ChatModelEnum, LLMFacade


class BaseAISystem:
    @staticmethod
    def load_messages(config: dict, key: str):
        """Load the template in the config into chat messages
        The Human message is templated as {input}

        Example:

        ```yaml
        ExamplePrompt1:
            prompt: >
                This is a template
        ```
        """
        c = config[key]
        prompt = c.get("prompt")

        if isinstance(prompt, str):
            prompt_str = prompt + "\n[INST] {input} [/INST]\n"
            return PromptTemplate.from_template(template=prompt_str)
        else:
            raise Exception("Cannot load message templates")

    @staticmethod
    def load_messages_chat(config: dict, key: str) -> str:
        c = config[key]
        prompt = c.get("prompt")
        return prompt

    @staticmethod
    def do_llm_with_model(llm: LLMFacade, token: str, model: ChatModelEnum):
        def _do_llm(_messages: List[BaseMessage]):
            return llm.internal_chat(
                model=model,
                messages=_messages,
                internal_token=token,
            )

        return _do_llm
