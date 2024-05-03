from dataclasses import dataclass
from components.requests.children import CAdvancePayment, CAdvancePaymentOwner, CDeclarationRevenue


@dataclass
class CreateAdvancePaymentRequest:
    __slots__ = {"userID", "owner", "advancePaymentData"}
    userID: str
    owner: CAdvancePaymentOwner
    advancePaymentData: CAdvancePayment






