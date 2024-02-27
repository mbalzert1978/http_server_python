from http import HTTPMethod

from app.request import request_from_stream
from tests.resources import byte


def test_request_parser():
    result = request_from_stream(byte.REQUEST)
    assert str(result.method) == HTTPMethod.POST


def test_echo_request_parser():
    result = request_from_stream(byte.ECHO_REQUEST)
    assert str(result.method) == HTTPMethod.GET
