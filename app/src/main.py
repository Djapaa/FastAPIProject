import aioredis
from fastapi import FastAPI, APIRouter
from .api_v1.auth.routers import router as auth_router

app = FastAPI()
router = APIRouter(prefix='/api/v1')

router.include_router(prefix='/auth', tags=['Auth'], router=auth_router)

app.include_router(router=router)



