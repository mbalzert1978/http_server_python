import operator


class Headers:
    method: str
    version: str
    path: str
    route: tuple[str, ...]

    def __init__(self, data: bytes) -> None:
        encode_data = data.decode(encoding="utf-8").splitlines()
        self.route = tuple(route for route in self.path.split("/") if route) or ("/",)
        self.__init(encode_data)
        self.__init_dict(encode_data)

    def __init(self, parsed: list[str]) -> None:
        method, path, version = operator.getitem(parsed, 0).split()
        setattr(self, "method", method.strip())
        setattr(self, "path", path.strip())
        setattr(self, "version", version.strip())

    def __init_dict(self, parsed: list[str]) -> None:
        def set_kv(attr: str) -> tuple[str, str]:
            key, value = attr.split(":", 1)
            return key.strip(), value.strip()

        for attr in parsed[1:]:
            if not attr:
                break
            key, value = set_kv(attr)
            setattr(self, key, value)

    def __repr__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__!r})"

    def __str__(self) -> str:
        cls = type(self)
        return f"{cls.__name__}({self.__dict__})"
