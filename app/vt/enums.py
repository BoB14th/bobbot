from enum import Enum

class ResponseEnum(str, Enum):
    VT_ANALYSIS_SUCCESS = "IoC 분석에 성공했습니다."
    VT_REPORT_NOT_FOUND = "VT 리포트가 존재하지 않습니다."
    INVALID_IOC_TYPE = "지원되지 않는 IoC 타입입니다."