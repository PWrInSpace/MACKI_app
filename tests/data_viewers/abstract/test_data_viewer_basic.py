import pytest
from src.data_viewers import DataViewerBasic

NAME = "test"


@pytest.fixture
def data_viewer():
    return DataViewerBasic(NAME)


def test_init(data_viewer):
    assert data_viewer.title() == NAME


def test_update_data(data_viewer):
    with pytest.raises(NotImplementedError):
        data_viewer.update_data({})
