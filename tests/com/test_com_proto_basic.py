import pytest
from src.com.com_proto_basic import ComProtoBasic


@pytest.fixture
def com():
    return ComProtoBasic()


def test_connect(com: ComProtoBasic):
    with pytest.raises(NotImplementedError):
        com.connect()


def test_disconnect(com: ComProtoBasic):
    with pytest.raises(NotImplementedError):
        com.disconnect()


def test_write(com: ComProtoBasic):
    with pytest.raises(NotImplementedError):
        com.write("test")


def test_read(com: ComProtoBasic):
    with pytest.raises(NotImplementedError):
        com.read()


def test_is_connected(com: ComProtoBasic):
    with pytest.raises(NotImplementedError):
        com.is_connected()
