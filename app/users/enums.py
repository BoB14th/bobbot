from enum import Enum

class ResponseEnum(str, Enum):
    USER_PASSWORD_ERROR = "비밀번호가 틀렸습니다."
    USER_NOT_FOUND = "회원가입이 필요합니다."
    USER_JOIN_SUCCESS = "회원가입에 성공했습니다."
    USER_LOGIN_SUCCESS = "로그인에 성공했습니다."
    USER_ALREADY_EXISTS = "유저가 이미 존재합니다."