from pydantic.dataclasses import dataclass
from components.enums import RateEnum, QuarterEnum


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


@dataclass
class CAdvancePaymentOwner:
    lastName: str  # фамилия
    firstName: str  # имя
    patronymic: str = None  # отчество


@dataclass
class CAdvancePayment:
    authorityCode: str  # код налоговой инспекции
    inn: int
    oktmo: str  # Код, присвоенный территории муниципального образования или населенному пункту, входящему в его состав
    revenue: int  # Сумма платежа
    quarter: QuarterEnum  # НомерМесКварт
    reportingYear: str  # отчётный год
    kbk: str  # КБК
    legalEntityID: str = None
