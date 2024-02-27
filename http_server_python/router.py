import typing
from dataclasses import dataclass, field
from http import HTTPMethod

from http_server_python.handler import not_found
from http_server_python.headers import Request
from http_server_python.response import Response

Handler = typing.Callable[[Request], Response]


@dataclass
class Router:
    routes: dict[str, dict[str, Handler]] = field(default_factory=dict)

    def add_route(
        self,
        handler: Handler,
        route: str = "/",
        method: HTTPMethod = HTTPMethod.GET,
    ) -> typing.Self:
        self.routes.setdefault(method, {}).setdefault(route, handler)
        return self

    def handle_route(self, request: Request) -> Response:
        return self.routes.get(request.method, {}).get(request.route.route, not_found)(
            request
        )
