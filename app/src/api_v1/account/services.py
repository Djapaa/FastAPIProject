
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from starlette import status


from .schemas import UserPartialUpdateSerializer
from ..auth.models import User
from ..general_services import get_object


class UserCRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int):
        subq = (
            select(
                func.count(User.voted).label('count_voted')
            )
            .join(
                User.voted,
                isouter=True,
            )
            .filter(
                User.id == user_id
            )
            .group_by(
                User.id
            )
            .subquery()
        )
        query = (
            select(
                User.id,
                User.username,
                User.is_stuff,
                User.is_superuser,
                User.is_active,
                User.is_verified,
                User.created_at,
                User.descriptions,
                User.balance,
                User.gender,
                User.email_not,
                User.avatar,
                subq.c.count_voted
            )
            .filter(
                User.id == user_id
            )
        )

        instance = await self.session.execute(query)
        instance_mapping = instance.mappings().one_or_none()
        if not instance_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User does not exist'
            )
        return instance_mapping

    async def partial_update(self, user_id, updated_data: UserPartialUpdateSerializer, current_user: User):
        target_user = await get_object(self.session, user_id, User)
        if not check_user_permissions(current_user, target_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='dont have permission'
            )
        target_user.username = updated_data.username or target_user.username
        target_user.gender = updated_data.gender or target_user.gender
        target_user.email_not = updated_data.email_not or target_user.email_not
        target_user.descriptions = updated_data.descriptions or target_user.descriptions
        self.session.add(target_user)
        try:
            await self.session.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with such username already exists'
            )
        return await self.get(user_id)


def check_user_permissions(current_user: User, target_user: User):
    # Пользователь является самим собой
    if current_user.id == target_user.id:
        return True
    # Админ и Супер админ может производить действия надо обычными пользователями
    if (current_user.is_stuff or current_user.is_superuser) and not target_user.is_stuff and not target_user.is_superuser:
        return True
    # Супер админ может все
    if current_user.is_superuser:
        return True
    return False
