from dataclasses import dataclass
from components.responses.children import CDeclaration


@dataclass
class CreateDeclarationResponse:
    __slots__ = {"declarationID"}
    declarationID: str


@dataclass
class GetDeclarationsResponse:
    __slots__ = {"declarations"}
    declarations: list[CDeclaration]
