from fastapi import APIRouter, Depends
from app.common.models.request import IoCRequest
from app.common.models.response import ResponseResult, IoCResponse
from app.logs import log_access
from app.database import SessionFactory
from app.utils.auth import get_api_key
from app.vt.vt_service import VtService
from fastapi.responses import JSONResponse
from functools import lru_cache

router = APIRouter()

@lru_cache()
def get_vt_service() -> VtService:
    return VtService(SessionFactory)

@router.post("/analysis", response_model=ResponseResult[IoCResponse], dependencies=[Depends(log_access), Depends(get_api_key)])
async def analyze_ioc_route(req:IoCRequest, vs: VtService = Depends(get_vt_service)):
    result = await vs.analyze_ioc(req.ioc)
    return JSONResponse(content=result.model_dump(exclude_none=True))