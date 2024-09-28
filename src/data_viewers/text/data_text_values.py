from src.data_viewers.abstract.data_viewer_basic import DataViewerBasic


class DataTextValues(DataViewerBasic):
    def __init__(self, name: str = ""):
        super().__init__(name)

    def update_data(self, data_dict: dict[str, any]):
        pass
