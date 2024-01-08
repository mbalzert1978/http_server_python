import dataclasses
from app import request


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

    async def generate_response(self) -> bytes:
        return bytes(self)


@dataclasses.dataclass
class Index(HttpResponse):
    async def generate_response(self) -> bytes:
        return bytes(self)


@dataclasses.dataclass
class TypeMixing:
    _type: str = dataclasses.field(default="")


@dataclasses.dataclass
class TextMixing(TypeMixing):
    _type: str = dataclasses.field(default="text/plain", init=False)


@dataclasses.dataclass
class Echo(HttpResponse, TextMixing):
    async def generate_response(self) -> bytes:
        for index, path in enumerate(self.data.headers.route):
            if path != "echo":
                continue
            echo = "/".join(self.data.headers.route[index + 1 :])
            break
        return (
            f"{super().__str__()}"
            f"Content-Type: {self._type}{self._nl}"
            f"Content-Length: {len(echo)}"
            f"{self._nl}{self._nl}{echo}"
        ).encode()


@dataclasses.dataclass
class NotFound(HttpResponse):
    _code: int = 404
    _status: str = "NOT FOUND"

    async def generate_response(self) -> bytes:
        return bytes(self)


@dataclasses.dataclass
class UserAgent(HttpResponse, TextMixing):
    async def generate_response(self) -> bytes:
        user_agent = getattr(self.data.headers, "User-Agent")
        return (
            f"{super().__str__()}"
            f"Content-Type: {self._type}{self._nl}"
            f"Content-Length: {len(user_agent)}{self._nl}{self._nl}"
            f"{user_agent}"
        ).encode()


def response_factory(request: request.HttpRequest) -> HttpResponse:
    if "echo" in set(request.headers.route):
        return Echo(request)
    if "user-agent" in set(request.headers.route):
        return UserAgent(request)
    if request.headers.route == ("/",):
        return Index(request)
    return NotFound(request)
