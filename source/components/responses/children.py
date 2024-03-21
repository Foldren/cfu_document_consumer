from dataclasses import dataclass, field
from decimal import Decimal
from dataclasses_json import DataClassJsonMixin


@dataclass
class CDeclaration:
    __slots__ = {"currentValue", "prevValue"}
    name: str
    inn: str
    date: str
    status: str = field()
    url: str
