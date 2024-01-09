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
        body: str | dict = operator.getitem(parsed, -1)
        if not body:
            body = {}
        if isinstance(body, str):
            if not isjson(body):
                setattr(self,"body", body)
                return
            setattr(self, "body", json.loads(body))
            return
        if isinstance(body, dict):
            setattr(self, "body", body)
            return
        if isinstance(body, bytes):
            setattr(self, "body", body)
        raise ValueError(f"Invalid body type: {type(body)}")

    def __repr__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__!r})"

    def __str__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__})"

def isjson(s: str) -> bool:
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False