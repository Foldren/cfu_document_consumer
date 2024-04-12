from dataclasses import dataclass
from components.enums import StatusEnum, DocumentTypeEnum


@dataclass
class CDocument:
    id: int
    name: str
    inn: int
    date: str
    status: StatusEnum  # статус формирования декларации
    documentType: DocumentTypeEnum
    xlsxUrl: str = None
    xmlUrl: str = None
