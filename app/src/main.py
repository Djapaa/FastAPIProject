
from sqladmin import Admin
from sqladmin import ModelView, Admin

from .api_v1.composition.models import *
from .config.database import engine
from fastapi import FastAPI, APIRouter
from .api_v1.auth.models import *

from .api_v1.auth.routers import router as auth_router
from .api_v1.composition.routers import router as composition_router

app = FastAPI()
admin = Admin(app, engine)


router = APIRouter(prefix='/api/v1')

router.include_router(prefix='/auth', tags=['Auth'], router=auth_router)

router.include_router(prefix='/composition', tags=['Composition'], router=composition_router)

app.include_router(router=router)






# Модели для админки
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username]

class UserTokenAdmin(ModelView, model=Token):
    column_list = [Token.id, Token.access_token, Token.user_id, Token.expire_date]

class CompositionAdmin(ModelView,model=Composition):
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


admin.add_view(UserAdmin)
admin.add_view(UserTokenAdmin)

admin.add_view(CompositionAdmin)
admin.add_view(TagsAdmin)
admin.add_view(StatusAdmin)
admin.add_view(TypeAdmin)
admin.add_view(AgeratingAdmin)
admin.add_view(GenreAdmin)


