import dataclasses
from pathlib import Path

from app import request


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
        if isinstance(self.data.body, bytes):
            self.file_path.write_bytes(self.data.body)

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


def response_factory(request: request.HttpRequest) -> HttpResponse:
    match request.header.route:
        case ("/",):
            return Index(request)
        case ("echo", *_):
            return Echo(request)
        case ("user-agent", *_):
            return UserAgent(request)
        case ("files", filename) if request.header.method == "GET":
            if not (file_path := request._directory / filename).exists():
                return NotFound(request)
            return Files(request, file_path)
        case ("files", filename) if request.header.method == "POST":
            return Writer(request, request._directory / filename)
        case _:
            return NotFound(request)
