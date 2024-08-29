class VmbCameraMock:
    def __init__(self, camera_id: str) -> None:
        self._camera_id = camera_id

    def get_id(self) -> str:
        return self._camera_id
