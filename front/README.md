# LINE-AI-Demo - FRONT END

This is the development document for FRONT END for [LINE-AI-DEMO](/README.md) project.

## Development

### Prerequisites

- Node >= 20 with NPM installed

General FE development can use the alpha Back End server. You need to be in the LINE internal network to connect to this server.

The server status can be check with this end point:

```bash
curl https://ai.line-alpha.me/healthz
```

### Setup

Because this application using [LIFF - LINE Front-end Framework](https://developers.line.biz/en/docs/liff/overview/), we need to setup the hosting that serve `https` and register the application ID with LIFF framework.

I already setup with the domain `local-line-ai-demo.line-alpha.me`.

During development you need to setup your local hosts name to resolve to this domain.

```bash
sudo vi /etc/hosts
```

Add this line into the file

```
127.0.0.1       local-line-ai-demo.line-alpha.me
```

### Start local development

```bash
npm install
npm run dev -- --mode alpha
```

This will use to the alpha server as Back end API.

## Roadmap

(under construction)
