import contextlib
import operator
import socket

HOST = "127.0.0.1"
PORT = 4221


def main() -> None:
    server_socket = get_listener()
    con: socket.socket
    con, _address = server_socket.accept()
    with contextlib.closing(con) as con:
        while data := con.recv(1024):
            lines = data.decode(encoding="utf-8").split("\r\n")
            _method, path, _http_version = operator.getitem(lines, 0).split()
            print(_method, path, _http_version)
            if path == "/":
                con.sendall(ok_200())
            else:
                con.sendall(not_found_404())


def ok_200() -> bytes:
    return "HTTP/1.1 200 OK\r\n\r\n".encode()


def not_found_404() -> bytes:
    return "HTTP/1.1 404 NOT FOUND\r\n\r\n".encode()


def get_listener(
    address: str = HOST, port: int = PORT, *, reuse_port=True
) -> socket.socket:
    return socket.create_server(address=(address, port), reuse_port=reuse_port)


if __name__ == "__main__":
    main()
