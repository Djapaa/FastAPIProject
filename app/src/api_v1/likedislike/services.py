from typing import TypeVar, Type
from pydantic import BaseModel
from fastapi import HTTPException, Request
from starlette import status
from sqlalchemy import select, func, cast, Integer
from sqlalchemy.orm import contains_eager, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from ..composition.services import check_obj_in_db
from .models import LikeDislike
from ..auth.models import Model

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class VoteCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = LikeDislike

    async def get_vote(self, voted_model: Type[Model], voted_obj_id: int, user_id: int):
        query = (
            select(self.model)
            .join(voted_model)
            .filter(
                voted_model.id == voted_obj_id,
                self.model.user_id == user_id
            )
        )
        instance = await self.session.scalar(query)
        if not instance:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'{voted_model.__name__} not found')
        return instance

    async def create_vote(self, voted_model: Type[Model], voted_obj_id: int, vote_type: bool, user_id: int):
        vote_type = 1 if vote_type else -1
        await check_obj_in_db(self.session, voted_obj_id, voted_model)
        obj_id = {f'{voted_model.__name__.lower()}_id': voted_obj_id}
        try:
            vote_instance = await self.get_vote(voted_model, voted_obj_id, user_id)
            if vote_instance.vote is not vote_type:
                vote_instance.vote = vote_type
                await self.session.commit()
                result = vote_type
            else:
                await self.session.delete(vote_instance)
                await self.session.commit()
                result = None
        except HTTPException:
            vote_instance = self.model(user_id=user_id, vote=vote_type, **obj_id)
            self.session.add(vote_instance)
            await self.session.commit()
            result = vote_type

        score = await self.session.scalar(select(func.sum(self.model.vote)).filter_by(**obj_id))

        return {
            'score': score,
            'vote': result
        }