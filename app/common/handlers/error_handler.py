from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.common.models.response import ResponseResult
from app.common.enums import ResponseEnum

def setup_exception_handlers(app):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        response = ResponseResult(
            result_code = ResponseEnum(exc.status_code),
            error_msg=str(exc.detail)
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=response.model_dump(exclude_none=True)
        )
    
    @app.exception_handler(Exception)
    async def not_found_exception_handler(request: Request, exc):
        response = ResponseResult(
            result_code = ResponseEnum.INTERVAL_SERVER_ERROR,
            error_msg="서버 내부 오류가 발생했습니다."
        )

        return JSONResponse(
            status_code=500,
            content=response.model_dump(exclude_none=True)
        )