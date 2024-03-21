from enum import IntEnum, Enum


class RateEnum(IntEnum):
    ONE = 1
    SIX = 6


class StatusEnum(str, Enum):
    process = 'process'
    success = 'success'
    error = 'error'
