from enum import Enum

class ResponseEnum(str, Enum):
    INVALID_CREDENTIAL="유효하지 않은 크레덴셜입니다."
    SUMMARY_FAIL = "본문을 찾지 못해 요약할 수 없었어요."
    EMPTY_RESPONSE = "빈 응답을 받았어요."