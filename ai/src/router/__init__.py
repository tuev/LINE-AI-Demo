from fastapi import FastAPI
from .auth_router import auth_router
from .usage_router import usage_router
from .document_router import document_router
from .ai_router import ai_router


def router_attach(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(usage_router)
    app.include_router(document_router)
    app.include_router(ai_router)
