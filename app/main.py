import contextlib
import socket

import model

HOST = "127.0.0.1"
PORT = 4221


def main() -> None:
    server_socket = get_listener()
    con: socket.socket
    con, _address = server_socket.accept()
    with contextlib.closing(con) as con:
        while data := con.recv(1024):
            request = model.parse(data)
            con.sendall(bytes(model.get(request)))


def get_listener(
    address: str = HOST, port: int = PORT, *, reuse_port=True
) -> socket.socket:
    return socket.create_server(address=(address, port), reuse_port=reuse_port)


if __name__ == "__main__":
    main()
