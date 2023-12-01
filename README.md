# LINE-AI-Demo

This demo project serves as the foundation for the LINE Vietnam AI Study Group. The objective of this group is to create a final demonstration product, using this project as a means for learning and development.

In the future, we aim to apply this setup to better Hardware and Backend infrastructure.

# Development

## Build and run with docker compose

```bash
docker compose up -d --build
```

If already built. Just need:

```bash
docker compose -f docker-compose.base.yaml -f docker-compose.dev.yaml up -d
```

To run the environment

```bash
docker exec -it line-ai-demo-ai-1 bash
```

To serve server line-ai (run this command inside the container)

```bash
sh run-dev.sh
```

## Frontend

Built with [Vue](https://vuejs.org) and [Vuetify](https://vuetifyjs.com/). And deployed to [Cloudflare Page](https://pages.cloudflare.com/).

Frontend development does not need to build and run the local Docker if it is not necessary.

More information inside the [front/README.md](/front/README.md)

## Vector database

[pgvector](https://github.com/pgvector/pgvector)

Using PostgreSQL with Vector database plugin.

### Create Vector plugin

The image we use already support vectors. We just need to activate it using the SQL below.

```SQL
CREATE EXTENSION vector;
```

## Object Storage - Minio as S3 service

[Minio](https://min.io/)

Create new access and secret key for S3 and setup it in .env file.

Create new bucket with name `lvn-ai-demo`

## Environment file .env

Example:

```
LIFF_CLIENT_ID=
S3_ENDPOINT=minio:9000
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_REGION=local
OPENAI_KEY=
```

# License

[MIT](https://opensource.org/licenses/MIT)

Copyright (c) 2023-, Quang Tran.
