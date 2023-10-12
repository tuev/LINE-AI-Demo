from typing import List

from langchain.prompts import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import BaseMessage


class BaseAISystem:
    @staticmethod
    def load_messages(config: dict, key: str):
        """Load the template in the config into chat messages
        The Human message is templated as {input}

        Example:

        ```yaml
        PromptKey1: >
            This is a template

            {format_instructions}

        PromptKey2:
            prompt: >
                This is another template

                {format_instructions}

            few_shots:
                - type: human
                  message: I'm human
                - type: ai
                  message: Hi human. I am AI.

            input: {question}
        ```
        """
        prompt = config[key]

        if isinstance(prompt, str):
            return ChatPromptTemplate.from_messages(
                [
                    SystemMessagePromptTemplate.from_template(prompt),
                    HumanMessagePromptTemplate.from_template("{input}"),
                ]
            )
        elif isinstance(prompt, dict) and prompt.get("prompt", None) is not None:
            system_template = prompt.get("prompt", "")
            system_prompt = SystemMessagePromptTemplate.from_template(system_template)
            human_input_template = prompt.get("input", "{input}")
            human_input = HumanMessagePromptTemplate.from_template(human_input_template)

            few_shots: List[BaseMessage] = []
            for fs in config[key].get("few_shots", []):
                msg_type = fs.get("type")
                msg_text: str = fs.get("message")
                msg_text = msg_text.replace("{", "{{").replace("}", "}}")
                if msg_type == "human":
                    msg = HumanMessagePromptTemplate.from_template(msg_text)
                elif msg_type == "ai":
                    msg = AIMessagePromptTemplate.from_template(msg_text)
                else:
                    raise Exception(f"unknown message type {msg_type}")

                few_shots.append(msg.format())

            return ChatPromptTemplate.from_messages(
                [
                    system_prompt,
                    *few_shots,
                    human_input,
                ]
            )
        else:
            raise Exception("Cannot load BaseAISystem message templates")
