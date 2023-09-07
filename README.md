# LINE-AI-Demo

This demo project serves as the foundation for the LINE Vietnam AI Study Group. The objective of this group is to create a final demonstration product, using this project as a means for learning and development.

In the future, we aim to apply this setup to better Hardware and Backend infrastructure.

# Development

## Install llama.cpp

[https://github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)

Recommend system: Macbook Metal ie: M1, M2 chips

NOTE: Not working with Intel + AMD chips. You need to tinker the setup yourself. I found it really hard to get the AMD working.

## Download the LLM Model

Currently, I'm trying with Code LLAMA. But your are free to try new models. Just need to point the server to the downloaded model.

Recommend link: [https://huggingface.co/TheBloke/CodeLlama-13B-Instruct-GGUF](https://huggingface.co/TheBloke/CodeLlama-13B-Instruct-GGUF)

## Run the LLM

```bash
cd llama.cpp
./server -m ~/Sync/learn-ai/models/codellama-13b-instruct.Q5_K_M.gguf -ngl 32
```

## Build and run with docker compose

```bash
docker compose up -d --build
```

If already built. Just need:

```base
docker compose up -d
```

## Vector database

### Create Vector plugin

```SQL
CREATE EXTENSION vector;
```

## Frontend

Built with sveltekit. And deployed to Cloudflare Page.

More information inside the [front/README.md](/front/README.md)

# License

[MIT](https://opensource.org/licenses/MIT)

Copyright (c) 2023-, Quang Tran.
