from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
import yaml

from repository.helpers import print_prompt
from repository.llm_facade import ChatModelEnum, LLMFacade
from systems.base_ai_ystem import BaseAISystem


class CodeRepo:
    def __init__(self, llm: LLMFacade):
        self.llm = llm

        with open("/app/src/prompts/code.yaml") as f:
            config = yaml.safe_load(f)

        self._completion_prompt = BaseAISystem.load_messages(config, "Completion")

    def completion(self, query: str):
        prompt = self._completion_prompt.format(input=query)
        print_prompt(prompt)
        return self.llm.completion_local_llm(prompt)

    def internal_chat(
        self,
        model: ChatModelEnum,
        internal_token: str,
    ):
        messages = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    "You are ChatGPT, a large language model trained by OpenAI. Follow the user's instructions carefully. Respond using markdown.",  # noqa: E501
                ),
                HumanMessagePromptTemplate.from_template(
                    "Write bash script to read from file"
                ),
                AIMessagePromptTemplate.from_template(
                    """\
```bash
cat file_name.txt
```

This script use `cat` command to output the content fo the file file_name.txt to the standard output.
"""  # noqa: E501
                ),
                HumanMessagePromptTemplate.from_template(
                    "Write python script to read file"
                ),
                AIMessagePromptTemplate.from_template(
                    """\
Certainly! Here's an example of a Python script that reads a file:

```python
file_name = "file_name.txt"

# Open the file in read mode
with open(file_name, 'r') as file:
    # Read the contents of the file
    file_contents = file.read()

    # Print the contents
    print(file_contents)
```

In this script, we use the `open` function to open the file in read mode (`'r'`). Then, we use the `read` method to read the contents of the file and store them in the `file_contents` variable. Finally, we print the contents to the console. The `with` statement is used to automatically close the file after reading.
"""  # noqa: E501
                ),
                HumanMessagePromptTemplate.from_template(
                    "Give me the same thing for Rust"
                ),
            ]
        )

        # resp = self.llm.internal_chat_stream(
        #     messages.format_prompt().to_messages(),
        #     model,
        #     internal_token,
        #     max_length,
        #     token_limit,
        # )
        # for i in resp:
        #     print(i)

        print(
            self.llm.internal_chat(
                messages.format_prompt().to_messages(),
                model,
                internal_token,
            )
        )
