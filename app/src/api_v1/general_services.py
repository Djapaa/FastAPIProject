import os
from typing import Type
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
import aiofiles

from ..config.model import Model
from ..config.settings import settings


async def get_object(session: AsyncSession, obj_id: int, model: Type['Model']):
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
