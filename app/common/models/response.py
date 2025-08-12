from typing import Optional, Generic, TypeVar
from pydantic import BaseModel
from app.common.enums import ResponseEnum

T = TypeVar("T")

class ResponseResult(BaseModel, Generic[T]):
    result_code: ResponseEnum
    result_msg: Optional[str] = None
    error_msg: Optional[str] = None
    data: Optional[T] = None

    class Config:
        exclude_unset = True
        exclude_none = True
        use_enum_values = True

class IoCResponse(BaseModel):
    ioc: str
    type: str
    malicious_score: int
    suggested_threat_label: Optional[str] = None
    vendor_count: int