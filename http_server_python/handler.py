import json
from http import HTTPStatus
from pathlib import Path

from http_server_python.headers import Request
from http_server_python.response import Response, ResponseBuilder

INDENT = 4
BUILDER = ResponseBuilder().add_version().add_code().add_status()


def not_found(_: Request) -> "Response":
    return (
        ResponseBuilder()
        .add_version()
        .add_code(HTTPStatus.NOT_FOUND)
        .add_status("NOT FOUND")
        .add_type()
        .add_body("")
        .build()
    )


def index(_: Request) -> "Response":
    return BUILDER.add_type().build()


def echo(request: Request) -> "Response":
    return BUILDER.add_type().add_body("/".join(request.route.values)).build()


def user_agent(request: Request) -> "Response":
    return (
        BUILDER.add_type()
        .add_header(request.headers)
        .add_body(request.headers.get("user-agent"))
        .build()
    )


def get_files(request: Request, directory: Path) -> "Response":
    try:
        file = (directory / request.route.values.pop()).read_text()
    except OSError:
        return not_found(request)
    else:
        return BUILDER.add_type("application/octet-stream").add_body(file).build()


def post_files(request: Request, directory: Path) -> "Response":
    match request.body:
        case bytes():
            body = request.body
        case str():
            body = request.body.encode()
        case dict() | list():
            body = json.dumps(request.body, indent=INDENT).encode()
        case _:
            return not_found(request)
    try:
        _ = (directory / request.route.values.pop()).write_bytes(body)
    except OSError:
        return not_found(request)
    else:
        return (
            ResponseBuilder()
            .add_version()
            .add_code(HTTPStatus.CREATED)
            .add_status("CREATED")
            .add_type()
            .add_body("")
            .build()
        )
