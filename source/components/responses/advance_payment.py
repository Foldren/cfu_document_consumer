from dataclasses import dataclass


@dataclass
class CreateAdvancePaymentResponse:
    __slots__ = {"advancePaymentID"}
    advancePaymentID: str
