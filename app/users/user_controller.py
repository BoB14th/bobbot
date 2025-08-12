from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.common.models.response import ResponseResult
from app.users import user_service
import app.schema as schema
from app.logs import log_access
from sqlalchemy.orm import Session
from app.database import db
from app.utils.auth import get_api_key

router = APIRouter()

@router.post("/login/", response_model=ResponseResult, dependencies=[Depends(log_access), Depends(get_api_key)])
def login(user: schema.Login, dbsession: Session = Depends(db.get_session)):
    result = user_service.userLogin(user.email, user.password, dbsession)
    return JSONResponse(content=result.model_dump(exclude_none=True))

@router.post("/join/", response_model=ResponseResult, dependencies=[Depends(log_access), Depends(get_api_key)])
def post_create_user(user: schema.UserCreate, dbsession: Session = Depends(db.get_session)):
    result = user_service.userJoin(user, dbsession)
    return JSONResponse(content=result.model_dump(exclude_none=True))