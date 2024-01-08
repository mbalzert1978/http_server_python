from dataclasses import dataclass, field
import operator


@dataclass
class Request:
    data: bytes
    http_version: str = field(init=False)
    method: str = field(init=False)
    path: str = field(init=False)

    def __post_init__(self) -> None:
        self.parse()

    def parse(self) -> None:
        lines = self.data.decode(encoding="utf-8").split("\r\n")
        self.method, self.path, self.http_version = operator.getitem(lines, 0).split()
