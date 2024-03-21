from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class RpcResponse(DataClassJsonMixin):
    fileName: str
