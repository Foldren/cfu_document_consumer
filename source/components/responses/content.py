from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class UploadFileResponse(DataClassJsonMixin):
    __slots__ = {"fileName"}
    fileName: str  # ссылка на файл
