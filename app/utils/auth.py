from fastapi import Security, HTTPException
from app.config import conf
from app.common.enums import ResponseEnum as code
from app.utils.enums import ResponseEnum as detail
from fastapi.security.api_key import APIKeyHeader

API_KEY = conf['apikey']
API_KEY_NAME = "api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key: str= Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=code.FORBIDDEN.value, detail=detail.INVALID_CREDENTIAL.value
        )