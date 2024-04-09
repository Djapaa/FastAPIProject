from typing import Annotated

from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from .config.database import get_async_session
from .api_v1.auth.routers import router as auth_router

app = FastAPI()

app.include_router(prefix='/auth', tags=["Auth"],router=auth_router)



# @app.get("/items/")
# async def read_items(session: AsyncSession = Depends(get_async_session)):
#     res = await session.execute(text('select now()'))
#     print(res.scalar())
#
# class Checker:
#     def __init__(self, model: BaseModel):
#         self.model = model
#
#     def __call__(self, data: str = Form(...)):
#         try:
#             return self.model.model_validate_json(data)
#         except ValidationError as e:
#             raise HTTPException(
#                 detail=jsonable_encoder(e.errors()),
#                 status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             )
# class PydanticFile(BaseModel):
#     name: str
#     age: int
# @app.post("/files/")
# async def create_file( file: Annotated[list[bytes], File()], user: PydanticFile = Depends(Checker(PydanticFile)),):
#     return {'msg': 'ok'}







