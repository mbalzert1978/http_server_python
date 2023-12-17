import socket


def parse_request(request: bytes) -> str:
    req_str = request.decode()
    lines = req_str.split("\r\n")
    print(lines)


def main() -> None:
    server_socket = create_server()
    client_socket, _ = server_socket.accept()
    request = client_socket.recv(1024)
    response = parse_request(request)
    response = "HTTP/1.1 200 OK\r\n\r\n"
    client_socket.sendall(response.encode())
    client_socket.close()


def create_server(
    address: str = "127.0.0.1", port: int = 4221, *, reuse_port=True
) -> socket.socket:
    return socket.create_server(address=(address, port), reuse_port=reuse_port)


if __name__ == "__main__":
    main()
