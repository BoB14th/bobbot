from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.common.models.response import ResponseResult
import app.schema as schema
from app.logs import log_access
from app.database import SessionFactory
from app.utils.auth import get_api_key
from .user_service import UserService
from functools import lru_cache

router = APIRouter()

@lru_cache()
def get_vt_service() -> UserService:
    return UserService(SessionFactory)

@router.post("/login/", response_model=ResponseResult, dependencies=[Depends(log_access), Depends(get_api_key)])
def login(user: schema.Login, userService: UserService = Depends(get_vt_service)):
    result = userService.user_login(user.email, user.password)
    return JSONResponse(content=result.model_dump(exclude_none=True))

@router.post("/join/", response_model=ResponseResult, dependencies=[Depends(log_access), Depends(get_api_key)])
def post_create_user(user: schema.UserCreate, userService: UserService = Depends(get_vt_service)):
    result = userService.userJoin(user)
    return JSONResponse(content=result.model_dump(exclude_none=True))