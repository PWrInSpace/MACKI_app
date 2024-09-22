from enum import Enum


class MacusWidgetState(Enum):
    """This class represents the MacusWidget state
    """
    DISCONNECTED = 0
    CONNECTED = 1
    MISSING = 2
