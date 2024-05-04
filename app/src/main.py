from sqladmin import ModelView, Admin
from starlette.authentication import requires
from fastapi import FastAPI, APIRouter, Request
from typing import Tuple, List
from fastapi import Request

from .api_v1.composition.models import *
from .config.database import engine
from .api_v1.auth.models import *
from .api_v1.auth.routers import router as auth_router
from .api_v1.composition.routers import router as composition_router
from .api_v1.comment.routers import router as comment_router
from .api_v1.likedislike.routers import router as like_dislike_router
from .api_v1.chapter.routers import router as chapter_router
from .api_v1.account.router import router as account_router

app = FastAPI()
admin = Admin(app, engine)

router = APIRouter(prefix='/api/v1')

router.include_router(prefix='/auth', tags=['Auth'], router=auth_router)

router.include_router(prefix='/composition', tags=['Composition'], router=composition_router)

router.include_router(prefix='/comment', tags=['Comment'], router=comment_router)

router.include_router(prefix='/vote', tags=['Vote'], router=like_dislike_router)

router.include_router(prefix='/composition', tags=['Chapter'], router=chapter_router)

router.include_router(prefix='/account', tags=['Account'], router=account_router)

app.include_router(router=router)


# Модели для админки
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username]


class UserTokenAdmin(ModelView, model=Token):
    column_list = [Token.id, Token.access_token, Token.user_id, Token.expire_date]


class CompositionAdmin(ModelView, model=Composition):
    pass


class TagsAdmin(ModelView, model=CompositionTag):
    column_list = [CompositionTag.id, CompositionTag.name]


class StatusAdmin(ModelView, model=CompositionStatus):
    column_list = [CompositionStatus.id, CompositionStatus.name]


class GenreAdmin(ModelView, model=CompositionGenre):
    column_list = [CompositionGenre.id, CompositionGenre.name]


class AgeratingAdmin(ModelView, model=CompositionsAgeRating):
    column_list = [CompositionsAgeRating.id, CompositionsAgeRating.name]


class TypeAdmin(ModelView, model=CompositionType):
    column_list = [CompositionType.id, CompositionType.name]


class ChapterAdmin(ModelView, model=Chapter):
    column_list = [Chapter.id, Chapter.is_published]


class UserCompositionRelationAdmin(ModelView, model=UserCompositionRelation):
    column_list = [UserCompositionRelation.id,
                   UserCompositionRelation.rating,
                   UserCompositionRelation.bookmark]



class LikeDislikeAdmin(ModelView, model=LikeDislike):
    column_list = [LikeDislike.id, LikeDislike.user_id, LikeDislike.chapter_id]


admin.add_view(UserAdmin)
admin.add_view(UserTokenAdmin)

admin.add_view(CompositionAdmin)
admin.add_view(TagsAdmin)
admin.add_view(StatusAdmin)
admin.add_view(TypeAdmin)
admin.add_view(AgeratingAdmin)
admin.add_view(GenreAdmin)
admin.add_view(ChapterAdmin)
admin.add_view(UserCompositionRelationAdmin)
admin.add_view(LikeDislikeAdmin)

