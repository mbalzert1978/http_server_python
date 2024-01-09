import argparse
import asyncio
import contextlib
import functools
from asyncio import streams
from pathlib import Path

from app import request, response

HOST = "127.0.0.1"
PORT = 4221
SHARE = Path.cwd() / "share"


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
    with contextlib.closing(writer):
        while data := await reader.read(2048):
            _request = request.HttpRequest(data)
            _request._directory = directory
            _response = response.response_factory(_request)
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
