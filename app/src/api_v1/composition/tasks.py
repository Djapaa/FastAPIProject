import asyncio

from celery import shared_task

from .models import Composition, UserCompositionRelation
from ..chapter.models import Chapter
from ..likedislike.models import LikeDislike
from ...config.database import async_session_factory
from sqlalchemy import select, distinct, func, bindparam, update


async def calculate_bookmarks_ratings_votes_task():
    async with async_session_factory() as session:
        subq = (
            select(
                Composition.id,
                func.coalesce(func.round(func.avg(UserCompositionRelation.rating), 1), 0).label('avg_rating'),
                func.count(distinct(UserCompositionRelation.bookmark)).label('count_bookmarks'),
                func.count(distinct(UserCompositionRelation.rating)).label('count_rating'),
                func.count(distinct(LikeDislike.vote)).label('total_votes')
            )
            .join(
                UserCompositionRelation, Composition.id == UserCompositionRelation.composition_id,
                isouter=True
            )
            .join(
                Chapter, Composition.id == Chapter.composition_id,
                isouter=True
            )
            .join(
                LikeDislike, Chapter.id == LikeDislike.chapter_id,
                isouter=True
            )
            .group_by(Composition.id)
            .cte()
        )
        query = (
            select(
                subq
            )
        )
        composition = await session.execute(query)
        composition = composition.mappings().all()

        await session.execute(update(Composition), composition)
        await session.commit()

@shared_task(name='calculate_bookmarks_ratings_votes_task')
def calculate_bookmarks_ratings_votes():
    """
    Таска считает и обновляет поля: count_rating, avg_rating, count_bookmarks, total_votes в модели Composition
    """
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(calculate_bookmarks_ratings_votes_task())



    # async with get_async_session() as session:
    #     composition = await session.execute(query)
    #     composition = composition.mappings().all()

