from __future__ import annotations

import dataclasses
import json
import typing
from pathlib import Path

from app import request

from .headers import Request

CRLF = "\r\n"


@dataclasses.dataclass
class TypeMixing:
    _type: str = dataclasses.field(default="")


@dataclasses.dataclass
class TextMixing(TypeMixing):
    _type: str = dataclasses.field(default="text/plain", init=False)


@dataclasses.dataclass
class JsonMixing(TypeMixing):
    _type: str = dataclasses.field(default="application/json", init=False)


@dataclasses.dataclass
class OctetMixing(TypeMixing):
    _type: str = dataclasses.field(default="application/octet-stream", init=False)


@dataclasses.dataclass
class HttpResponse:
    data: request.HttpRequest
    _code: int = dataclasses.field(default=200, init=False)
    _version: str = dataclasses.field(default="HTTP/1.1", init=False)
    _status: str = dataclasses.field(default="OK", init=False)
    _nl: str = dataclasses.field(default="\r\n", init=False)

    def __str__(self) -> str:
        return f"{self._version} {self._code} {self._status}{self._nl}"

    def __bytes__(self) -> bytes:
        return str(self).encode()

    async def to_bytes(self) -> bytes:
        return bytes(self)


@dataclasses.dataclass
class Index(HttpResponse, TextMixing):
    def __str__(self) -> str:
        """
        HTTP/1.1 200 OK
        Content-Type: text/plain
        Content-Length: 11

        curl/7.64.1
        """
        return f"{super().__str__()}{self._nl}"


@dataclasses.dataclass
class Echo(HttpResponse, TextMixing):
    def __str__(self) -> str:
        for index, path in enumerate(self.data.header.route):
            if path != "echo":
                continue
            echo = "/".join(self.data.header.route[index + 1 :])
            break
        return (
            f"{super().__str__()}"
            f"Content-Type: {self._type}{self._nl}"
            f"Content-Length: {len(echo)}"
            f"{self._nl}{self._nl}{echo}"
        )


@dataclasses.dataclass
class Files(HttpResponse, OctetMixing):
    data: request.HttpRequest
    file_path: Path
    _body: bytes = dataclasses.field(default=b"", init=False)

    def __post_init__(self) -> None:
        self.read_file()

    def read_file(self) -> None:
        self._body = self.file_path.read_bytes()

    def __str__(self) -> str:
        """
        HTTP/1.1 200 OK
        Content-Type: application/octet-stream
        Content-Length: 11

        curl/7.64.1
        """
        return (
            f"{super().__str__()}"
            f"Content-Type: {self._type}{self._nl}"
            f"Content-Length: {len(self._body)}{self._nl}{self._nl}"
            f"{self._body.decode(encoding='utf-8')}"
        )


@dataclasses.dataclass
class Writer(HttpResponse, TextMixing):
    data: request.HttpRequest
    file_path: Path
    _code: int = dataclasses.field(default=201, init=False)
    _status: str = dataclasses.field(default="CREATED", init=False)

    def __post_init__(self) -> None:
        self.write_file()

    def write_file(self) -> None:
        match self.data.body:
            case bytes():
                body = self.data.body
            case str():
                body = self.data.body.encode(encoding="utf-8")
            case dict() | list():
                body = json.dumps(self.data.body, indent=4).encode(encoding="utf-8")
            case _:
                raise ValueError(f"Invalid body type: {type(self.data.body)}")
        self.file_path.write_bytes(body)

    def __str__(self) -> str:
        """
        HTTP/1.1 201 Created
        Content-Type: text/plain
        Content-Length: 27
        Connection: closed

        File successfully uploaded.
        """
        msg = "File successfully uploaded."
        return (
            f"{super().__str__()}"
            f"Content-Type: {self._type}{self._nl}"
            f"Content-Length: {len(msg)}{self._nl}{self._nl}"
            f"{msg}"
        )


@dataclasses.dataclass
class NotFound(HttpResponse, TextMixing):
    _code: int = 404
    _status: str = "NOT FOUND"

    def __str__(self) -> str:
        return (
            f"{super().__str__()}"
            f"Content-Type: {self._type}{self._nl}"
            f"Content-Length: 0{self._nl}{self._nl}"
        )


@dataclasses.dataclass
class UserAgent(HttpResponse, TextMixing):
    def __str__(self) -> str:
        """
        HTTP/1.1 200 OK
        Content-Type: text/plain
        Content-Length: 11

        curl/7.64.1
        """
        user_agent = getattr(self.data.header, "User-Agent")
        return (
            f"{super().__str__()}"
            f"Content-Type: {self._type}{self._nl}"
            f"Content-Length: {len(user_agent)}{self._nl}{self._nl}"
            f"{user_agent}"
        )


def not_found(_: Request) -> "Response":
    return ResponseBuilder().add_version().add_code(404).add_status("NOT FOUND").build()


def index(_: Request) -> "Response":
    return ResponseBuilder().add_version().add_code().add_status().build()


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


def files(request: Request, directory: Path) -> "Response":
    builder = ResponseBuilder().add_version()
    file_name: str = request.route.values.pop()
    try:
        file = (directory / file_name).read_text()
    except Exception:
        response = not_found(None)
    response = (
        builder.add_code(200)
        .add_status("OK")
        .add_type("application/octet-stream")
        .add_body(file)
        .build()
    )
    print(response)
    return response


@dataclasses.dataclass
class Response:
    code: int
    version: str
    status: str
    headers: dict[str, str] | None = None
    body: typing.Any | None = None

    def __str__(self) -> str:
        if self.headers:
            headers_str = CRLF.join(
                f"{key}: {value}" for key, value in self.headers.items()
            )
        else:
            headers_str = CRLF
        if self.body:
            body_str = f"{CRLF}{CRLF}{self.body}"
        else:
            body_str = CRLF

        return f"{self.version} {self.code} {self.status}{CRLF}{headers_str}{body_str}"

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
