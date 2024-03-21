from dataclasses import dataclass
from components.requests.children import (CCreateDeclarationBase, CCreateDeclarationOwner,
                                          CCreateDeclarationDeclaration, CCreateDeclarationRevenue)


@dataclass
class DeclarationCreateDeclarationRequest:
    userID: str
    base: CCreateDeclarationBase
    owner: CCreateDeclarationOwner
    declaration: CCreateDeclarationDeclaration
    revenue: CCreateDeclarationRevenue





