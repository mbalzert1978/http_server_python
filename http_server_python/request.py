import json

from http_server_python.headers import Request, RequestBuilder

CRLF = "\r\n"


def request_from_stream(
    stream: bytes,
    builder: RequestBuilder = RequestBuilder(),
) -> Request:
    headers, body = _get_headers_body(stream)
    method, url, version = _get_method_url_version(headers.pop(0))
    builder.add_method(method).add_url(url).add_version(version)
    builder.add_headers(dict(_get_header(header) for header in headers))
    builder.add_body(_parse_body(body.pop(0)))
    return builder.build()


def _get_headers_body(stream: bytes) -> tuple[list[str], list[str]]:
    request = stream.decode().rsplit(CRLF)
    split_ = request.index("")
    req = request[:split_]
    body = request[split_ + 1 :]
    return req, body


def _parse_body(body: str | dict | bytes) -> dict | str | bytes:
    if not body:
        return {}
    try:
        return json.loads(body)  # type: ignore[arg-type]
    except json.JSONDecodeError:
        return body


def _get_header(line: str) -> tuple[str, str]:
    key, value = line.split(":", 1)
    return key.strip(), value.strip()


def _get_method_url_version(lines: str) -> tuple[str, str, str]:
    method, path, version = lines.split()
    return method.strip(), path.strip(), version.strip()
