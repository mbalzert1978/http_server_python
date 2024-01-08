from dataclasses import dataclass, field
import operator
from typing import NamedTuple


class Request(NamedTuple):
    method: str
    full_path: str


@dataclass
class HttpResponse:
    data: Request
    _code: int = field(default=200, init=False)
    _version: str = field(default="HTTP/1.1", init=False)
    _status: str = field(default="OK", init=False)
    _nl: str = field(default="\r\n", init=False)

    def __str__(self) -> str:
        return f"{self._version} {self._code} {self._status}{self._nl}"

    def __bytes__(self) -> bytes:
        return str(self).encode()


@dataclass
class Index(HttpResponse):
    def __str__(self) -> str:
        return f"{super().__str__()}{self._nl}"


@dataclass
class Echo(HttpResponse):
    def __str__(self) -> str:
        _slash, _path, echo = self.data.full_path.partition("echo/")
        return f"{super().__str__()}Content-Length: {len(echo)}{self._nl}{self._nl}{echo}"


@dataclass
class NotFound(HttpResponse):
    _code: int = 404
    _status: str = "NOT FOUND"

    def __str__(self) -> str:
        return f"{self._version} {self._code} {self._status}{self._nl}{self._nl}"


def parse(data: bytes) -> Request:
    lines = data.decode().split("\r\n")
    method, path, _ = operator.getitem(lines, 0).split()
    return Request(method, path)


def get(request: Request) -> HttpResponse:
    if request.full_path.startswith("/echo"):
        return Echo(request)
    if request.full_path == "/":
        return Index(request)
    return NotFound(request)
