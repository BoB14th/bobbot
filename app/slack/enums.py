from enum import Enum

class ResponseEnum(str, Enum):
    ANALYSIS_FAIL = "내부 오류로 분석에 실패했어요. 잠시 후 다시 시도해 주세요."
    NOT_MATCH_REGEX = "현재 기능은 분석밖에 없어요.. `예시 입력 : 분석 1.1.1.1`"

