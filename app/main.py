import asyncio
import contextlib
from asyncio.streams import StreamReader, StreamWriter

from app import request
from app import response

HOST = "127.0.0.1"
PORT = 4221


async def handle_connection(reader: StreamReader, writer: StreamWriter) -> None:
    with contextlib.closing(writer) as writer:
        while data := await reader.read(1024):
            _request = request.HttpRequest(data)
            _response = response.response_factory(_request)
            writer.write(await _response.to_bytes())
            await writer.drain()


async def main() -> None:
    server = await asyncio.start_server(handle_connection, HOST, PORT, reuse_port=True)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
