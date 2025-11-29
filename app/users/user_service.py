from fastapi.exceptions import HTTPException
from app.common.models.response import ResponseResult
from app.common.enums import ResponseEnum as common
from app.users.enums import ResponseEnum as response
from sqlalchemy.orm import Session, sessionmaker
import app.schema as schema
import app.crud as crud
import hashlib
import base64

class UserService:
    def __init__(self, session_factory: sessionmaker):
        self._session_factory = session_factory
    
    def user_login(self, email:str, password:str):
        db: Session = self._session_factory()
        try:
            user = crud.find_user_by_email(db, email)
            if user is None:
                raise HTTPException(
                    status_code=common.NOT_FOUND.value,
                    detail=response.USER_NOT_FOUND.value,
                )

            if self._verify_password(user, password):
                data = {"user_id": user.id}
                return ResponseResult(
                    result_code=common.SUCCESS.value,
                    result_msg=response.USER_LOGIN_SUCCESS.value,
                    data=data,
                )
            else:
                raise HTTPException(
                    status_code=common.UNAUTHORIZED.value,
                    detail=response.USER_PASSWORD_ERROR.value,
                )
        finally:
            db.close()
        

    def user_join(self, user: schema.UserCreate) -> ResponseResult:
        db: Session = self._session_factory()
        try:
            if crud.exist_user_by_email(db, user.email):
                raise HTTPException(
                    status_code=common.BAD_REQUEST.value,
                    detail=response.USER_ALREADY_EXISTS.value,
                )

            new_user = crud.create_user(db, user)  
            data = {"user_id": new_user.id}
            return ResponseResult(
                result_code=common.SUCCESS.value,
                result_msg=response.USER_JOIN_SUCCESS.value,
                data=data,
            )
        finally:
            db.close()

    @staticmethod
    def _verify_password(user, password: str) -> bool:
        try:
            salt = base64.b64decode(user.salt)
            hashed_original = base64.b64decode(user.hashed_password)
        except Exception:
            return False

        hashed_check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
        return hashed_check == hashed_original
    

