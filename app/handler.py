import json
from pathlib import Path

from app.headers import Request
from app.response import Response, ResponseBuilder

INDENT = 4


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
    try:
        file = (directory / request.route.values.pop()).read_text()
    except OSError:
        return not_found(request)
    else:
        return (
            ResponseBuilder()
            .add_version()
            .add_code(200)
            .add_status("OK")
            .add_type("application/octet-stream")
            .add_body(file)
            .build()
        )


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
            .add_code(201)
            .add_status("CREATED")
            .add_type()
            .add_body("")
            .build()
        )
