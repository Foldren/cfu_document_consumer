from dataclasses import dataclass
from components.enums import StatusEnum


@dataclass
class CDeclaration:
    name: str
    inn: str
    date: str
    status: StatusEnum
    url: str = None
