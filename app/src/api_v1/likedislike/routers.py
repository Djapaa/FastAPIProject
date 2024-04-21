from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends

from .schemas import VoteChapterSerializer, VoteCommentSerializer
from .services import VoteCRUD
from ..auth.schemas import UserInfoSerializer
from ..auth.services import get_current_user
from ..chapter.models import Chapter
from ...config.database import get_async_session

router = APIRouter()


@router.post('/chapter/')
async def chapter_vote(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        vote_obj: VoteChapterSerializer,
        current_user: Annotated[UserInfoSerializer, Depends(get_current_user)],
):
    vote_crud = VoteCRUD(session)
    return await vote_crud.create_vote(Chapter, vote_obj.chapter_id, vote_obj.vote_type, current_user.id)
