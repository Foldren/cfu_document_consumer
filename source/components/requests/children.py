from pydantic.dataclasses import dataclass
from components.requests.enums import RateEnum


@dataclass
class CCreateDeclarationBase:
    inn: str
    rate: RateEnum
    legalEntityID: str = None
    employeesCount: int = None  # -


@dataclass
class CCreateDeclarationOwner:
    __slots__ = {"lastName", "firstName", "patronymic", "taxPayer", "phoneNumber"}
    lastName: str
    firstName: str
    patronymic: str
    taxPayer: str  # -
    phoneNumber: str


@dataclass
class CCreateDeclarationDeclaration:
    adjustmentNumber: str  # -
    taxPeriod: str  # -
    reportingYear: str
    authorityCode: str  # -
    locationCode: str  # -
    oktmoCurrent: str
    oktmoOld: str = None  # -
    oktmoChangeDate: str = None  # -


@dataclass
class CCreateDeclarationRevenue:
    __slots__ = {"threeMonths", "sixMonths", "nineMonths", "twelveMonths"}
    threeMonths: int
    sixMonths: int
    nineMonths: int
    twelveMonths: int
