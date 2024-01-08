import json
import operator
from app import headers


class HttpRequest:
    headers: headers.Headers
    body: dict

    def __init__(self, data: bytes) -> None:
        encode_data = data.decode(encoding="utf-8").splitlines()
        self.headers = headers.Headers(data)
        self.__init_body(encode_data)

    def __init_body(self, parsed: list[str]) -> None:
        body: str | dict = operator.getitem(parsed, -1)
        if not body:
            body = {}
        if isinstance(body, str):
            setattr(self, "body", json.loads(body))
            return
        if isinstance(body, dict):
            setattr(self, "body", body)
            return
        raise ValueError(f"Invalid body type: {type(body)}")

    def __repr__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__!r})"

    def __str__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__})"