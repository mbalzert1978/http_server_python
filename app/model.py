import dataclasses
import json
import operator


class Headers:
    method: str
    version: str
    path: str
    route: tuple[str, ...]

    def __init__(self, data: bytes) -> None:
        encode_data = data.decode(encoding="utf-8").splitlines()
        self.__init(encode_data)
        self.__init_dict(encode_data)
        self.__init_route()

    def __init(self, parsed: list[str]) -> None:
        method, path, version = operator.getitem(parsed, 0).split()
        setattr(self, "method", method.strip())
        setattr(self, "path", path.strip())
        setattr(self, "version", version.strip())

    def __init_route(self) -> None:
        raw_route = tuple(route for route in self.path.split("/") if route)
        if not raw_route:
            self.route = ("/",)
            return
        self.route = raw_route

    def __init_dict(self, parsed: list[str]) -> None:
        def set_kv(attr: str) -> tuple[str, str]:
            key, value = attr.split(":", 1)
            return key.strip(), value.strip()

        for attr in parsed[1:]:
            if not attr:
                break
            key, value = set_kv(attr)
            setattr(self, key, value)

    def __repr__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__!r})"

    def __str__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__})"


class HttpRequest:
    headers: Headers
    body: dict

    def __init__(self, data: bytes) -> None:
        encode_data = data.decode(encoding="utf-8").splitlines()
        self.headers = Headers(data)
        self.__init_body(encode_data)

    def __init_body(self, parsed: list[str]) -> None:
        body: str | dict = operator.getitem(parsed, -1)
        if not body:
            body = {}
        if isinstance(body, str):
            setattr(self, "body", json.loads(body))
            return
        if isinstance(body, dict):
            setattr(self, "body", body)
            return
        raise ValueError(f"Invalid body type: {type(body)}")

    def __repr__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__!r})"

    def __str__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__})"


@dataclasses.dataclass
class HttpResponse:
    data: HttpRequest
    _code: int = dataclasses.field(default=200, init=False)
    _version: str = dataclasses.field(default="HTTP/1.1", init=False)
    _status: str = dataclasses.field(default="OK", init=False)
    _nl: str = dataclasses.field(default="\r\n", init=False)

    def __str__(self) -> str:
        return f"{self._version} {self._code} {self._status}{self._nl}"

    def __bytes__(self) -> bytes:
        return str(self).encode()


@dataclasses.dataclass
class Index(HttpResponse):
    def __str__(self) -> str:
        return f"{super().__str__()}{self._nl}"


@dataclasses.dataclass
class Echo(HttpResponse):
    _type: str = dataclasses.field(default="text/plain", init=False)


@dataclasses.dataclass
class NotFound(HttpResponse):
    _code: int = 404
    _status: str = "NOT FOUND"

    def __str__(self) -> str:
        return f"{self._version} {self._code} {self._status}{self._nl}{self._nl}"


def get(request: HttpRequest) -> HttpResponse:
    if "echo" in set(request.headers.route):
        return Echo(request)
    if request.headers.route == ("/",):
        return Index(request)
    return NotFound(request)
