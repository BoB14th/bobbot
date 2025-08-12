from fastapi.exceptions import HTTPException
from app.common.models.response import ResponseResult
from app.common.enums import ResponseEnum as common
from app.users.enums import ResponseEnum as response
from sqlalchemy.orm import Session
import app.schema as schema
import app.crud as crud
import hashlib
import base64

def userLogin(email:str, password:str, dbsession: Session):
    user = crud.find_user_by_email(dbsession, email)
    if user is None:
        raise HTTPException(status_code=common.NOT_FOUND.value, detail=response.USER_NOT_FOUND.value)
    
    data = {
        "user_id": user.id
    }

    if verify_password(user, password):
        return ResponseResult(result_code=common.SUCCESS.value, result_msg=response.USER_LOGIN_SUCCESS.value, data=data)
    else:
        raise HTTPException(status_code=common.NOT_FOUND.value, detail=response.USER_PASSWORD_ERROR.value)
    
def verify_password(user, password: str) -> bool:
    # Base64 디코딩
    salt = base64.b64decode(user.salt)
    hashed_original = base64.b64decode(user.hashed_password)
    # 입력 비밀번호 해싱
    hashed_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return hashed_check == hashed_original

def userJoin(user: schema.UserCreate, dbsession: Session):
    if crud.exist_user_by_email(dbsession, user.email):
        raise HTTPException(status_code=common.BAD_REQUEST.value, detail=response.USER_ALREADY_EXISTS.value)
    
    new_user = crud.create_user(dbsession, user)

    data = {
        "user_id": new_user.id
    }

    return ResponseResult(result_code=common.SUCCESS.value, result_msg=response.USER_JOIN_SUCCESS.value, data=data)