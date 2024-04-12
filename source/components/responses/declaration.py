from dataclasses import dataclass


@dataclass
class CreateDeclarationResponse:
    __slots__ = {"declarationID"}
    declarationID: str
