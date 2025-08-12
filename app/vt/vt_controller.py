from fastapi import APIRouter, Depends
from app.common.models.request import IoCRequest
from app.common.models.response import ResponseResult, IoCResponse
import app.schema as schema
from app.logs import log_access
from sqlalchemy.orm import Session
from app.database import db
from app.utils.auth import get_api_key
from app.vt.vt_service import analyze_ioc
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/analysis", response_model=ResponseResult[IoCResponse], dependencies=[Depends(log_access), Depends(get_api_key)])
async def analyze_ioc_route(req:IoCRequest, db: Session = Depends(db.get_session)):
    result = await analyze_ioc(req.ioc, db)
    return JSONResponse(content=result.model_dump(exclude_none=True))