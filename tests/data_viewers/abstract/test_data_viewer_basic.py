import pytest
from src.data_viewers import DataViewerBasic

NAME = "test"


@pytest.fixture
def data_viewer():
    return DataViewerBasic(NAME)


def test_init(data_viewer):
    assert data_viewer.title() == NAME