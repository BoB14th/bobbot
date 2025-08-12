from enum import Enum

class ResponseEnum(int, Enum):
    SUCCESS = 200
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERVAL_SERVER_ERROR = 500
    BAD_REQUEST = 400