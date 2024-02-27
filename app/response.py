from __future__ import annotations

import dataclasses
import json
import typing
from pathlib import Path

from app.headers import Request

CRLF = "\r\n"


def not_found(_: Request) -> "Response":
    return (
        ResponseBuilder()
        .add_version()
        .add_code(404)
        .add_status("NOT FOUND")
        .add_type()
        .add_body("")
        .build()
    )


def index(_: Request) -> "Response":
    return ResponseBuilder().add_version().add_code().add_status().add_type().build()


def echo(request: Request) -> "Response":
    return (
        ResponseBuilder()
        .add_version()
        .add_code()
        .add_status()
        .add_type()
        .add_body(request.url.lstrip("/echo/"))
        .build()
    )


def user_agent(request: Request) -> "Response":
    return (
        ResponseBuilder()
        .add_version()
        .add_code()
        .add_status()
        .add_type()
        .add_header(request.headers)
        .add_body(request.headers.get("User-Agent"))
        .build()
    )


def get_files(request: Request, directory: Path) -> "Response":
    builder = ResponseBuilder().add_version()
    file_name: str = request.route.values.pop()
    try:
        file = (directory / file_name).read_text()
    except Exception:
        response = not_found(request)
    else:
        response = (
            builder.add_code(200)
            .add_status("OK")
            .add_type("application/octet-stream")
            .add_body(file)
            .build()
        )
    return response


def post_files(request: Request, directory: Path) -> "Response":
    builder = ResponseBuilder().add_version()
    body = _parse_body(request.body)
    file_name: str = request.route.values.pop()
    try:
        file = (directory / file_name).write_bytes(body)
    except Exception:
        response = not_found(request)
    else:
        response = (
            builder.add_code(200)
            .add_status("OK")
            .add_type("application/octet-stream")
            .add_body(file)
            .build()
        )
    return response


def _parse_body(body: typing.Any) -> bytes:
    match body:
        case bytes():
            return body
        case str():
            return body.encode(encoding="utf-8")
        case dict() | list():
            return json.dumps(body, indent=4).encode(encoding="utf-8")
        case _:
            raise ValueError(f"Invalid body type: {type(body)}")


@dataclasses.dataclass
class Response:
    code: int
    version: str
    status: str
    headers: dict[str, str] = dataclasses.field(default_factory=dict)
    body: typing.Any | None = None

    def __str__(self) -> str:
        status_line = f"{self.version} {self.code} {self.status}{CRLF}"
        header_lines = "".join(
            f"{key}: {value}{CRLF}" for key, value in self.headers.items()
        )
        return f"{status_line}{header_lines}{CRLF + self.body if self.body is not None else CRLF}"

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

    def add_code(self, code: int = 200) -> typing.Self:
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
