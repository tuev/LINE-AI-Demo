from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router import auth_router, code_router

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(code_router)
app.include_router(auth_router)


@app.get("/healthz")
async def healthz():
    return "healthy"
