from dataclasses import dataclass
from components.enums import StatusEnum


@dataclass
class CDeclaration:
    id: int
    name: str
    inn: int
    date: str
    status: StatusEnum
    url: str = None
