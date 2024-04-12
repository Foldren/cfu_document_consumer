from dataclasses import dataclass


@dataclass
class GetDocumentsRequest:
    __slots__ = {"userID"}
    userID: str


@dataclass
class RemoveDocumentRequest:
    __slots__ = {"id", "userID"}
    id: int
    userID: str
