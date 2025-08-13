from enum import Enum

class ResponseEnum(str, Enum):
    ANALYSIS_FAIL = "내부 오류로 분석에 실패했어요. 잠시 후 다시 시도해 주세요."
    NOT_MATCH_REGEX = "현재 기능은 분석밖에 없어요.. `예시 입력 : 분석 1.1.1.1`"
    WAIT_MENTION = " 님의 정보를 밥위키에서 가져오는 중이에요 ~~ :mag:"
    OPENAI_API_KEY_ERROR = "OPENAI_API_KEY가 설정되지 않아 요약 기능을 사용할 수 없어요."
    PAGE_NOT_FOUND = "페이지가 없거나 접근할 수 없어요 ㅠㅠ"
    SUMMARY_ERROR = "요약 중 오류가 발생했어요! "

