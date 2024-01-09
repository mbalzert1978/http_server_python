import json
import operator

from app import headers


class HttpRequest:
    header: headers.Headers
    body: dict | bytes

    def __init__(self, data: bytes) -> None:
        encode_data = data.decode(encoding="utf-8").splitlines()
        self.header = headers.Headers(data)
        self._directory = None
        self.__init_body(encode_data)

    def __init_body(self, parsed: list[str]) -> None:
        body: str | dict | bytes = operator.getitem(parsed, -1) or {}
        setattr(self, "body", json.loads(body) if isjson(body) else body)

    def __repr__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__!r})"

    def __str__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__})"


def isjson(s: str | dict | bytes) -> bool:
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False
