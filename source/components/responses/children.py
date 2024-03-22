from dataclasses import dataclass
from components.enums import StatusEnum


@dataclass
class CDeclaration:
    name: str
    inn: int
    date: str
    status: StatusEnum
    url: str = None
