from fastapi import HTTPException
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, contains_eager
from starlette import status

from .models import Composition, CompositionGenre, CompositionTag, CompositionStatus, CompositionType, \
    CompositionsAgeRating, UserCompositionRelation
from .schemas import CompositionCreateSerializer, Paginator, CompositionUpdateSerializer
from ..auth.models import User
from ..general_services import get_object, get_or_create
from ...config.database import async_session


class CompositionCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, composition_id: int):
        query = (
            select(Composition)
            .options(
                joinedload(Composition.status),
                joinedload(Composition.type),
                joinedload(Composition.age_rating),
                selectinload(Composition.composition_genres),
                selectinload(Composition.composition_tags)
            )
            .filter(Composition.id == composition_id)
        )

        composition = await self.session.scalar(query)
        if not composition:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'Composition not found')
        return composition

    async def get_paginate_and_filtered_list(
            self,
            paginator: Paginator,
            filter: Filter
    ):
        query = (
            select(Composition)
            .distinct()
            .join(Composition.composition_tags)
            .join(Composition.type)
            .join(Composition.status)
            .join(Composition.age_rating)
            .join(Composition.composition_genres)
            .options(contains_eager(Composition.type))
            .offset(paginator.offset)
            .limit(paginator.page_size)
        )
        query = filter.filter(query)
        query = filter.sort(query)
        compositions = await self.session.execute(query)
        return compositions.scalars().all()

    async def create(
            self,
            composition: CompositionCreateSerializer,
    ):
        composition_obj = Composition()

        composition_obj.title = composition.title
        composition_obj.slug = composition.slug
        composition_obj.english_title = composition.english_title
        composition_obj.another_name_title = composition.another_name_title
        composition_obj.descriptions = composition.descriptions
        composition_obj.year_of_creations = composition.year_of_creations

        new_status = await get_object(self.session, composition.status, CompositionStatus)
        composition_obj.status_id = new_status.id

        new_type = await get_object(self.session, composition.type, CompositionType)
        composition_obj.type_id = new_type.id

        new_agerating = await get_object(self.session, composition.age_rating, CompositionsAgeRating)
        composition_obj.age_rating_id = new_agerating.id

        new_genres = [await get_object(self.session, genre, CompositionGenre)
                      for genre in composition.genres]
        composition_obj.composition_genres = new_genres

        new_tags = [await get_object(self.session, tag, CompositionTag)
                    for tag in composition.tags]
        composition_obj.composition_tags = new_tags

        self.session.add(composition_obj)
        try:
            await self.session.commit()
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='composition already exists'
            )
        await self.session.refresh(composition_obj)
        return composition_obj

    async def partial_update(
            self,
            composition_id: int,
            composition: CompositionUpdateSerializer
    ):
        composition_obj = await self.get(composition_id)

        composition_obj.title = composition.title or composition_obj.title
        composition_obj.slug = composition.slug or composition_obj.slug
        composition_obj.english_title = composition.english_title or composition_obj.english_title
        composition_obj.another_name_title = composition.another_name_title or composition_obj.another_name_title
        composition_obj.descriptions = composition.descriptions or composition_obj.descriptions
        composition_obj.year_of_creations = composition.year_of_creations or composition_obj.year_of_creations

        if composition.status:
            new_status = await get_object(self.session, composition.status, CompositionStatus)
            composition_obj.status_id = new_status.id

        if composition.type:
            new_type = await get_object(self.session, composition.type, CompositionType)
            composition_obj.type_id = new_type.id
        if composition.age_rating:
            new_agerating = await get_object(self.session, composition.age_rating, CompositionsAgeRating)
            composition_obj.age_rating_id = new_agerating.id

        if composition.composition_genres:
            new_genres = [await get_object(self.session, genre, CompositionGenre)
                          for genre in composition.composition_genres]
            composition_obj.composition_genres = new_genres

        if composition.composition_tags:
            new_tags = [await get_object(self.session, tag, CompositionTag)
                        for tag in composition.composition_tags]
            composition_obj.composition_tags = new_tags

        self.session.add(composition_obj)
        await self.session.commit()
        return composition_obj

    async def _user_relation_add(
            self,
            composition_id: int,
            user_id: int,
            vote: int,
            vote_field_name: str
    ):
        await self.get(composition_id)
        instance, _ = await get_or_create(
            self.session,
            UserCompositionRelation,
            user_id=user_id,
            composition_id=composition_id
        )
        if not hasattr(instance, vote_field_name):
            raise AttributeError(f'attribute {vote_field_name}, does not exists')

        setattr(instance, vote_field_name, vote)
        self.session.add(instance)
        await self.session.commit()
        return instance

    async def rating_add(
            self,
            composition_id: int,
            user_id: int,
            vote: int
    ):
        return await self._user_relation_add(composition_id, user_id, vote, 'rating')

    async def bookmark_add(
            self,
            composition_id: int,
            user_id: int,
            vote: int
    ):
        return await self._user_relation_add(composition_id, user_id, vote, 'bookmark')


async def get_composition_readers(composition_id: int):
    async with async_session() as session:
        query = (

            select(
                User
            )
            .distinct()
            .select_from(
                User
            )
            .join(
                UserCompositionRelation
            )
            .options(
                selectinload(
                    User.evaluated_and_bookmark_compositions
                )
            )
            .filter(
                Composition.id == composition_id,
                UserCompositionRelation.bookmark != None
            )
        )
        chapter_instance = await session.scalars(query)
        return chapter_instance.all()