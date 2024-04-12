from enum import IntEnum, Enum


class RateEnum(IntEnum):
    one = 1
    six = 6


class QuarterEnum(IntEnum):
    one = 1
    two = 2
    three = 3
    four = 4


class StatusEnum(str, Enum):
    process = 'process'
    success = 'success'
    error = 'error'


class DocumentTypeEnum(str, Enum):
    declaration = 'declaration'
    advance_payment = 'advance_payment'
