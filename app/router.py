import typing
from dataclasses import dataclass, field

from app.headers import Request
from app.response import Response, not_found

Handler = typing.Callable[[Request], Response]


@dataclass
class Router:
    routes: dict[str, dict[str, Handler]] = field(default_factory=dict)

    def add_route(
        self,
        handler: Handler,
        route: str = "/",
        method: str = "GET",
    ) -> typing.Self:
        self.routes.setdefault(method, {}).setdefault(route, handler)
        return self

    def handle_route(self, request: Request) -> Response:
        return self.routes.get(request.method, {}).get(request.route.route, not_found)(
            request
        )
