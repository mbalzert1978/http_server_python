import contextlib
import socket

from app import request
from app import response

HOST = "127.0.0.1"
PORT = 4221


def main() -> None:
    server_socket = get_listener()
    con: socket.socket
    con, _address = server_socket.accept()
    with contextlib.closing(con) as con:
        while data := con.recv(1024):
            _request = request.HttpRequest(data)
            con.sendall(bytes(response.response_factory(_request)))


def get_listener(
    address: str = HOST, port: int = PORT, *, reuse_port=True
) -> socket.socket:
    return socket.create_server(address=(address, port), reuse_port=reuse_port)


if __name__ == "__main__":
    main()
