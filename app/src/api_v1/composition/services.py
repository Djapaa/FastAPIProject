import os
import aiofiles
from fastapi import HTTPException, UploadFile

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from typing import Type

from .schemas import CompositionCreateSerializer
from .models import Composition, CompositionGenre, CompositionTag, CompositionStatus, CompositionType, CompositionsAgeRating
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
    obj = await session.execute(query)
    obj = obj.scalar()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={
                                f'{model.__tablename__}': f'Invalid id {obj_id}, object not found'}
                            )
    return obj


async def create(
        composition: CompositionCreateSerializer,
        session: AsyncSession,
        image: UploadFile
):
    composition_image = await upload_image(image, 'composition')

    composition_obj = Composition()

    composition_obj.composition_image = composition_image
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


