from fastapi import FastAPI
from .auth_router import auth_router
from .code_router import code_router
from .usage_router import usage_router


def router_attach(app: FastAPI):
    app.include_router(code_router)
    app.include_router(auth_router)
    app.include_router(usage_router)
