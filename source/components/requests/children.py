from pydantic.dataclasses import dataclass
from components.enums import RateEnum


@dataclass
class CDeclarationBase:
    inn: str
    rate: RateEnum
    legalEntityID: str = None
    employeesCount: int = None  # -


@dataclass
class CDeclarationOwner:
    __slots__ = {"lastName", "firstName", "patronymic", "taxPayer", "phoneNumber"}
    lastName: str
    firstName: str
    patronymic: str
    taxPayer: str  # -
    phoneNumber: str


@dataclass
class CDeclarationDeclaration:
    adjustmentNumber: str  # -
    taxPeriod: str  # -
    reportingYear: str
    authorityCode: str  # -
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
