from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router import router_attach

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router_attach(app)


@app.get("/healthz")
async def healthz():
    return "healthy"
