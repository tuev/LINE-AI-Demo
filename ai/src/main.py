from fastapi import FastAPI

from router import code_router

app = FastAPI()

app.include_router(code_router)


@app.get("/healthz")
async def healthz():
    return "healthy"
