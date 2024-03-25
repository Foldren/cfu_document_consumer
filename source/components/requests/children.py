from pydantic.dataclasses import dataclass
from components.enums import RateEnum


@dataclass
class CDeclarationBase:
    inn: int
    rate: RateEnum
    createDate: str
    legalEntityID: str = None
    employeesCount: int = None


@dataclass
class CDeclarationOwner:
    lastName: str
    firstName: str
    taxPayer: str
    phoneNumber: str
    patronymic: str = None


@dataclass
class CDeclarationDeclaration:
    adjustmentNumber: str  # -
    taxPeriod: str  # -
    reportingYear: str
    authorityCode: str
    locationCode: str  # -
    oktmoCurrent: str
    oktmoOld: str = None  # -
    oktmoChangeDate: str = None  # -


@dataclass
class CDeclarationRevenue:
    __slots__ = {"threeMonths", "sixMonths", "nineMonths", "twelveMonths"}
    threeMonths: int
    sixMonths: int
    nineMonths: int
    twelveMonths: int
