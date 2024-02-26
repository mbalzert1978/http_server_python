import pydantic


class Body(pydantic.BaseModel):
    data: dict | bytes | str


class Json(Body):
    pass


class String(Body):
    pass


class Byte(Body):
    pass


class Header(pydantic.BaseModel):
    pass


class HttpRequest(pydantic.BaseModel):
    header: Header
    body: Body
