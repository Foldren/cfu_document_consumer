from pydantic.dataclasses import dataclass
from components.enums import RateEnum


@dataclass
class CDeclarationBase:
    inn: int
    rate: RateEnum
    createDate: str  # дата открытия ИП
    legalEntityID: str = None
    employeesCount: int = None  # кол-во сотрудников


@dataclass
class CDeclarationOwner:
    lastName: str  # фамилия
    firstName: str  # имя
    taxPayer: str  # поле налогоплатильщика
    phoneNumber: str
    patronymic: str = None  # отчество


@dataclass
class CDeclarationDeclaration:
    adjustmentNumber: str  # -
    taxPeriod: str  # -
    reportingYear: str  # отчётный год
    authorityCode: str  # код налоговой инспекции
    locationCode: str  # -
    oktmoCurrent: str  # код ОКТМО
    oktmoOld: str = None  # -
    oktmoChangeDate: str = None  # -


@dataclass
class CDeclarationRevenue:
    __slots__ = {"threeMonths", "sixMonths", "nineMonths", "twelveMonths"}
    threeMonths: int
    sixMonths: int
    nineMonths: int
    twelveMonths: int
