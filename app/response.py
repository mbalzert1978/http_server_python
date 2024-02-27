from __future__ import annotations

import dataclasses
import typing
from http import HTTPStatus

CRLF = "\r\n"


@dataclasses.dataclass
class Response:
    code: int
    version: str
    status: str
    headers: dict[str, str] = dataclasses.field(default_factory=dict)
    body: typing.Any | None = None

    def __str__(self) -> str:
        status_line = f"{self.version} {self.code} {self.status}"
        header_lines = "".join(
            f"{key}: {value}{CRLF}" for key, value in self.headers.items()
        )
        return (
            f"{status_line}{CRLF}{header_lines}"
            f"{CRLF + self.body if self.body is not None else CRLF}"
        )

    def __bytes__(self) -> bytes:
        return str(self).encode()

    async def to_bytes(self) -> bytes:
        return bytes(self)


@dataclasses.dataclass
class ResponseBuilder:
    code: int | None = None
    version: str | None = None
    status: str | None = None
    headers: dict[str, str] | None = None
    body: typing.Any | None = None

    def add_type(self, type_: str = "text/plain") -> typing.Self:
        self.add_header({"Content-Type": type_})
        return self

    def add_code(self, code: int = HTTPStatus.OK) -> typing.Self:
        self.code = code
        return self

    def add_version(self, version: str = "HTTP/1.1") -> typing.Self:
        self.version = version
        return self

    def add_status(self, status: str = "OK") -> typing.Self:
        self.status = status
        return self

    def add_header(self, headers: dict[str, str]) -> typing.Self:
        if self.headers is None:
            self.headers = {}
        self.headers |= headers
        return self

    def add_body(self, body: typing.Any):
        self.body = body
        self.add_header({"Content-Length": str(len(body))})
        return self

    def build(self) -> Response:
        return Response(**self.__dict__)
