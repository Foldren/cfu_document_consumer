from dataclasses import dataclass
from components.responses.children import CDocument


@dataclass
class GetDocumentsResponse:
    __slots__ = {"documents"}
    documents: list[CDocument]


@dataclass
class RemoveDocumentResponse:
    __slots__ = {"id"}
    id: int
