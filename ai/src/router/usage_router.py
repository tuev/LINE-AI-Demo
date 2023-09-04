from fastapi import APIRouter
from repository import usage_repo


usage_router = APIRouter(prefix="/usage")


@usage_router.get("/last_10")
async def last_10():
    results = usage_repo.last_usages(10)
    return [r.dict() for r in results]
