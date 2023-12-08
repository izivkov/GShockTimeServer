from enum import Enum


class WatchInfo:

    class model(Enum):
        B5600 = 1
        B2100 = 2
        UNKNOWN = 3

    def __init__(self) -> None:
        self.name = ""
        self.address = ""

    def set_name(self, name):
        self.name = name
        self.model = self.model.B5600 if "5600" in name else self.model.B2100

    def set_address(self, address):
        self.address = address


watch_info = WatchInfo()
