from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .config.database import get_async_session

app = FastAPI()

# async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
#     return {"q": q, "skip": skip, "limit": limit}



@app.get("/items/")
async def read_items(session: AsyncSession = Depends(get_async_session)):
    res = await session.execute(text('select * from test'))
    print(res.scalar())