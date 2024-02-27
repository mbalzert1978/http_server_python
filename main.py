import argparse
import asyncio
import contextlib
import functools
from asyncio import streams
from http import HTTPMethod
from pathlib import Path

from http_server_python.handler import echo, get_files, index, post_files, user_agent
from http_server_python.request import request_from_stream
from http_server_python.router import Router

HOST = "127.0.0.1"
PORT = 4221
SHARE = Path.cwd() / "share"
BUFSIZE = 4096


def parse_args():
    parser = argparse.ArgumentParser(description="Async Http Server Example")
    parser.add_argument("--host", default="127.0.0.1", help="Server host address.")
    parser.add_argument("--port", type=int, default=4221, help="Server port number.")
    parser.add_argument(
        "--directory",
        type=Path,
        help=(
            "The directory to serve files from. "
            "Defaults to the current working directory '/share'."
        ),
        default=SHARE,
    )
    return parser.parse_args()


async def handle_connection(
    reader: streams.StreamReader, writer: streams.StreamWriter, directory: Path
) -> None:
    router = (
        Router()
        .add_route(index, "/")
        .add_route(echo, "echo")
        .add_route(user_agent, "user-agent")
        .add_route(functools.partial(get_files, directory=directory), "files")
        .add_route(
            functools.partial(post_files, directory=directory),
            "files",
            HTTPMethod.POST,
        )
    )
    with contextlib.closing(writer):
        while data := await reader.read(BUFSIZE):
            _request = request_from_stream(data)
            _response = router.handle_route(_request)
            writer.write(await _response.to_bytes())
            await writer.drain()


async def main(args: argparse.Namespace) -> None:
    connection_handler = functools.partial(handle_connection, directory=args.directory)
    server = await asyncio.start_server(connection_handler, HOST, PORT, reuse_port=True)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
