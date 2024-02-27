import typing
from collections import namedtuple
from dataclasses import dataclass, field
from http import HTTPMethod

Route = namedtuple("Route", ["route", "values"])


def _generate_route(url: str = "/"):
    if url == "/":
        return Route("/", [])
    base, *values = [route for route in url.split("/") if route]
    return Route(base, values)


@dataclass
class Request:
    version: str
    method: HTTPMethod
    url: str
    headers: dict[str, str]
    route: Route = field(default_factory=_generate_route)
    body: typing.Any = field(default_factory=dict)


@dataclass
class RequestBuilder:
    method: HTTPMethod | None = None
    version: str | None = None
    url: str | None = None
    headers: dict[str, str] | None = None
    route: Route | None = None
    body: typing.Any = None

    def add_method(self, method: str = "GET") -> typing.Self:
        self.method = HTTPMethod(method)
        return self

    def add_version(self, version: str = "HTTP/1.1") -> typing.Self:
        self.version = version
        return self

    def add_url(self, url: str = "/") -> typing.Self:
        self.url = url
        self.route = _generate_route(url)
        return self

    def add_headers(self, headers: dict[str, str]) -> typing.Self:
        if self.headers is None:
            self.headers = {}
        self.headers |= headers
        return self

    def add_body(self, body: typing.Any = None) -> typing.Self:
        if body is None:
            body = {}
        self.body = body
        return self

    def build(self) -> Request:
        return Request(**self.__dict__)
