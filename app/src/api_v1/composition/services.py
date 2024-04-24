import os
from typing import Type

import aiofiles
from fastapi import HTTPException, UploadFile
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, contains_eager
from starlette import status

from .models import Composition, CompositionGenre, CompositionTag, CompositionStatus, CompositionType, \
    CompositionsAgeRating, UserCompositionRelation
from .schemas import CompositionCreateSerializer, CompositionDetailSerializer, Paginator, CompositionListSerializer, \
    CompositionUpdateSerializer
from ...config.model import Model
from ...config.settings import settings


async def upload_image(image: UploadFile, upload_subdir: str | None = None):
    if image.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type")

    if not upload_subdir:
        upload_subdir = ''
    upload_dir = os.path.join(settings.MEDIA_ROOT, upload_subdir)
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    dest = os.path.join(upload_dir, image.filename)

    content = await image.read()
    async with aiofiles.open(dest, 'wb') as out_file:
        await out_file.write(content)

    return dest


async def check_obj_in_db(session: AsyncSession, obj_id: int, model: Type['Model']):
    query = (
        select(model)
        .filter(model.id == obj_id)
    )
    obj = await session.scalar(query)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={
                                f'{model.__tablename__}': f'Invalid id {obj_id}, object not found'}
                            )
    return obj


async def create_new_composition(
        composition: CompositionCreateSerializer,
        session: AsyncSession,
):
    composition_obj = Composition()

    composition_obj.title = composition.title
    composition_obj.slug = composition.slug
    composition_obj.english_title = composition.english_title
    composition_obj.another_name_title = composition.another_name_title
    composition_obj.descriptions = composition.descriptions
    composition_obj.year_of_creations = composition.year_of_creations

    new_status = await check_obj_in_db(session, composition.status, CompositionStatus)
    composition_obj.status_id = new_status.id

    new_type = await check_obj_in_db(session, composition.type, CompositionType)
    composition_obj.type_id = new_type.id

    new_agerating = await check_obj_in_db(session, composition.age_rating, CompositionsAgeRating)
    composition_obj.age_rating_id = new_agerating.id

    for genre in composition.genres:
        res = await check_obj_in_db(session, genre, CompositionGenre)
        composition_obj.composition_genres.append(res)

    for tag in composition.tags:
        res = await check_obj_in_db(session, tag, CompositionTag)
        composition_obj.composition_tags.append(res)

    session.add(composition_obj)
    await session.commit()


async def get_composition_by_id(composition_id: int, session: AsyncSession) -> Composition:
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

    composition = await session.scalar(query)
    if not composition:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'Composition not found')
    return composition



async def get_all_composition(session: AsyncSession, paginator: Paginator, filter: Filter):
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
    compositions = await session.execute(query)
    return compositions.scalars().all()


async def get_composition_detail(composition_id: int, session: AsyncSession):
    composition = await get_composition_by_id(composition_id, session)
    return CompositionDetailSerializer.model_validate(composition, from_attributes=True)


async def get_composition_list(session: AsyncSession, paginator: Paginator, composition_filter):
    compositions = await get_all_composition(session, paginator, composition_filter)
    return [CompositionListSerializer.model_validate(composition, from_attributes=True) for composition in compositions]


async def partial_update_composition(composition_id: int,
                                     session: AsyncSession,
                                     composition: CompositionUpdateSerializer):
    composition_obj = await get_composition_by_id(composition_id, session)

    composition_obj.title = composition.title or composition_obj.title
    composition_obj.slug = composition.slug or composition_obj.slug
    composition_obj.english_title = composition.english_title or composition_obj.english_title
    composition_obj.another_name_title = composition.another_name_title or composition_obj.another_name_title
    composition_obj.descriptions = composition.descriptions or composition_obj.descriptions
    composition_obj.year_of_creations = composition.year_of_creations or composition_obj.year_of_creations

    if composition.status:
        new_status = await check_obj_in_db(session, composition.status, CompositionStatus)
        composition_obj.status_id = new_status.id

    if composition.type:
        new_type = await check_obj_in_db(session, composition.type, CompositionType)
        composition_obj.type_id = new_type.id
    if composition.age_rating:
        new_agerating = await check_obj_in_db(session, composition.age_rating, CompositionsAgeRating)
        composition_obj.age_rating_id = new_agerating.id

    if composition.composition_genres:
        for genre in composition.composition_genres:
            res = await check_obj_in_db(session, genre, CompositionGenre)
            composition_obj.composition_genres.append(res)

    if composition.composition_tags:
        for tag in composition.composition_tags:
            res = await check_obj_in_db(session, tag, CompositionTag)
            composition_obj.composition_tags.append(res)

    session.add(composition_obj)
    await session.commit()
    return CompositionDetailSerializer.model_validate(composition_obj, from_attributes=True)


async def get_or_create(session: AsyncSession, model, defaults=None, **kwargs):
    instance = await session.execute(select(model).filter_by(**kwargs))
    instance = instance.scalar_one_or_none()
    if instance:
        return instance, False
    else:
        kwargs |= defaults or {}
        instance = model(**kwargs)

        try:
            session.add(instance)
            await session.commit()
        except Exception:
            await session.rollback()
            instance = await session.execute(select(model).filter_by(**kwargs))
            instance = instance.scalar_one()
            return instance, False
        else:
            return instance, True


async def user_composition_relation_add(
        composition_id: int,
        user_id: int,
        session: AsyncSession,
        vote: int,
        vote_field_name: str
):
    await get_composition_by_id(composition_id, session)
    instance, _ = await get_or_create(
        session,
        UserCompositionRelation,
        user_id=user_id,
        composition_id=composition_id
    )
    if not hasattr(instance, vote_field_name):
        raise AttributeError(f'attribute {vote_field_name}, does not exists')

    setattr(instance, vote_field_name, vote)
    session.add(instance)
    await session.commit()
    return instance


async def rating_add(
        composition_id: int,
        user_id: int,
        session: AsyncSession,
        vote: int
):
    return await user_composition_relation_add(composition_id, user_id, session, vote, 'rating')


async def bookmark_add(
        composition_id: int,
        user_id: int,
        session: AsyncSession,
        vote: int
):
    return await user_composition_relation_add(composition_id, user_id, session, vote, 'bookmark')
