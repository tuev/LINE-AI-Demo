# LINE-AI-Demo

The Line AI demo is a project that leverages Large Language Models on consumer hardware. Its main goal is to exhibit the quality of these models, providing a practical tool for users to experience AI capabilities in real-time.

Furthermore, this demo is the starting point for the LINE VN AI Study Group. This group aims to build a final demonstration product, using this project as a learning and development opportunity, allowing them to explore the complexities of AI.

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

## Frontend

Built with sveltekit. And deployed to Cloudflare Page.

More information inside the [front/README.md](/front/README.md)
