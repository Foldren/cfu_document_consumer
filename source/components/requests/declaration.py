from dataclasses import dataclass
from components.requests.children import (CDeclarationBase, CDeclarationOwner,
                                          CDeclarationDeclaration, CDeclarationRevenue)


@dataclass
class CreateDeclarationRequest:
    __slots__ = {"userID", "base", "owner", "declaration", "revenue"}
    userID: str
    base: CDeclarationBase
    owner: CDeclarationOwner
    declaration: CDeclarationDeclaration
    revenue: CDeclarationRevenue


@dataclass
class GetDeclarationsRequest:
    __slots__ = {"userID"}
    userID: str


@dataclass
class RemoveDeclarationRequest:
    __slots__ = {"id", "userID"}
    id: int
    userID: str






