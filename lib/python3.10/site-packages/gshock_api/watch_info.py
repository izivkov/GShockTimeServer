from enum import Enum
from gshock_api.logger import logger

class WATCH_MODEL(Enum):
    GA = 1
    GW = 2
    DW = 3
    GMW = 4
    GPR = 5
    GST = 6
    MSG = 7
    GB001 = 8
    GBD = 9
    ECB = 10
    MRG = 11
    OCW = 12
    GB = 13
    GM = 14
    UNKNOWN = 20

class WatchInfo:
    def __init__(self):
        self.name = ""
        self.shortName = ""
        self.address = ""
        self.model = WATCH_MODEL.UNKNOWN

        # Default capabilities
        self.worldCitiesCount = 2
        self.dstCount = 3
        self.alarmCount = 5
        self.hasAutoLight = False
        self.hasReminders = False
        self.shortLightDuration = ""
        self.longLightDuration = ""
        self.weekLanguageSupported = True
        self.worldCities = True
        self.temperature = True
        self.batteryLevelLowerLimit = 15
        self.batteryLevelUpperLimit = 20

        self.alwaysConnected = False
        self.findButtonUserDefined = False
        self.hasPowerSavingMode = True
        self.hasDnD = False
        self.hasBatteryLevel = False

        # Model capability definitions (deduplicated)
        self.models = [
            {
                "model": WATCH_MODEL.GW,
                "worldCitiesCount": 6,
                "dstCount": 3,
                "alarmCount": 5,
                "hasAutoLight": False,
                "hasReminders": True,
                "shortLightDuration": "2s",
                "longLightDuration": "4s",
                "batteryLevelLowerLimit": 9,
                "batteryLevelUpperLimit": 19,
            },
            {
                "model": WATCH_MODEL.MRG,
                "worldCitiesCount": 6,
                "dstCount": 3,
                "alarmCount": 5,
                "hasAutoLight": False,
                "hasReminders": True,
                "shortLightDuration": "2s",
                "longLightDuration": "4s",
                "batteryLevelLowerLimit": 9,
                "batteryLevelUpperLimit": 19,
            },
            {
                "model": WATCH_MODEL.GMW,
                "worldCitiesCount": 6,
                "dstCount": 3,
                "alarmCount": 5,
                "hasAutoLight": True,
                "hasReminders": True,
                "shortLightDuration": "2s",
                "longLightDuration": "4s",
            },
            {
                "model": WATCH_MODEL.GST,
                "worldCitiesCount": 2,
                "dstCount": 1,
                "alarmCount": 5,
                "hasAutoLight": True,
                "hasReminders": True,
                "shortLightDuration": "1.5s",
                "longLightDuration": "3s",
            },
            {
                "model": WATCH_MODEL.GA,
                "worldCitiesCount": 2,
                "dstCount": 1,
                "alarmCount": 5,
                "hasAutoLight": True,
                "hasReminders": True,
                "shortLightDuration": "1.5s",
                "longLightDuration": "3s",
            },
            {
                "model": WATCH_MODEL.GB001,
                "worldCitiesCount": 2,
                "dstCount": 1,
                "alarmCount": 5,
                "hasAutoLight": True,
                "hasReminders": False,
                "shortLightDuration": "1.5s",
                "longLightDuration": "3s",
            },
            {
                "model": WATCH_MODEL.MSG,
                "worldCitiesCount": 2,
                "dstCount": 1,
                "alarmCount": 5,
                "hasAutoLight": True,
                "hasReminders": True,
                "shortLightDuration": "1.5s",
                "longLightDuration": "3s",
            },
            {
                "model": WATCH_MODEL.GPR,
                "worldCitiesCount": 2,
                "dstCount": 1,
                "alarmCount": 5,
                "hasAutoLight": True,
                "hasReminders": False,
                "shortLightDuration": "1.5s",
                "longLightDuration": "3s",
                "weekLanguageSupported": False,
            },
            {
                "model": WATCH_MODEL.DW,
                "worldCitiesCount": 2,
                "dstCount": 1,
                "alarmCount": 5,
                "hasAutoLight": True,
                "hasReminders": False,
                "shortLightDuration": "1.5s",
                "longLightDuration": "3s",
            },
            {
                "model": WATCH_MODEL.GBD,
                "worldCitiesCount": 2,
                "dstCount": 1,
                "alarmCount": 5,
                "hasAutoLight": True,
                "hasReminders": False,
                "shortLightDuration": "1.5s",
                "longLightDuration": "3s",
                "worldCities": False,
                "temperature": False,
            },
            {
                "model": WATCH_MODEL.ECB,
                "worldCitiesCount": 2,
                "dstCount": 1,
                "alarmCount": 5,
                "hasAutoLight": True,
                "hasReminders": False,
                "shortLightDuration": "1.5s",
                "longLightDuration": "3s",
                "worldCities": True,
                "temperature": False,
                "hasBatteryLevel": False,
                "alwaysConnected": True,
                "findButtonUserDefined": True,
                "hasPowerSavingMode": False,
                "hasDnD": True
            },
            {
                "model": WATCH_MODEL.UNKNOWN,
                "worldCitiesCount": 2,
                "dstCount": 1,
                "alarmCount": 5,
                "hasAutoLight": True,
                "hasReminders": False,
                "shortLightDuration": "1.5s",
                "longLightDuration": "3s",
            },
        ]

        # Build model→info lookup
        self.model_map = {entry["model"]: entry for entry in self.models}

    def set_name_and_model(self, name):
        self.name = name
        self.shortName = None
        self.model = WATCH_MODEL.UNKNOWN

        parts = self.name.split(" ")
        if len(parts) > 1:
            self.shortName = parts[1]

        if not self.shortName:
            return

        # Special case: exact match for ECB models
        if self.shortName in {"ECB-10", "ECB-20", "ECB-30"}:
            self.model = WATCH_MODEL.ECB
        else:
            # Ordered prefix-to-model mapping (longer prefixes first)
            prefix_map = [
                ("MSG", WATCH_MODEL.MSG),
                ("GPR", WATCH_MODEL.GPR),
                ("GBM", WATCH_MODEL.GA),
                ("GST", WATCH_MODEL.GST),
                ("GBD", WATCH_MODEL.GBD),
                ("GMW", WATCH_MODEL.GMW),
                ("DW",  WATCH_MODEL.DW),
                ("GA",  WATCH_MODEL.GA),
                ("GB",  WATCH_MODEL.GB),
                ("GM",  WATCH_MODEL.GM),
                ("GW",  WATCH_MODEL.GW),
                ("MRG", WATCH_MODEL.MRG),
                ("GMW", WATCH_MODEL.GMW),
            ]

            for prefix, model in prefix_map:
                if self.shortName.startswith(prefix):
                    self.model = model
                    break

        model_info = self.model_map.get(self.model)
        if not model_info:
            return

        # Set attributes with defaults
        self.hasReminders          = model_info.get("hasReminders", False)
        self.hasAutoLight          = model_info.get("hasAutoLight", False)
        self.alarmCount            = model_info.get("alarmCount", 0)
        self.worldCitiesCount      = model_info.get("worldCitiesCount", 0)
        self.dstCount              = model_info.get("dstCount", 0)
        self.shortLightDuration    = model_info.get("shortLightDuration", 0)
        self.longLightDuration     = model_info.get("longLightDuration", 0)
        self.weekLanguageSupported = model_info.get("weekLanguageSupported", True)
        self.worldCities           = model_info.get("worldCities", True)
        self.temperature           = model_info.get("temperature", True)
        self.batteryLevelLowerLimit= model_info.get("batteryLevelLowerLimit", 15)
        self.batteryLevelUpperLimit= model_info.get("batteryLevelUpperLimit", 20)
        self.alwaysConnected       = model_info.get("alwaysConnected", False)
        self.findButtonUserDefined = model_info.get("findButtonUserDefined", False)
        self.hasPowerSavingMode    = model_info.get("hasPowerSavingMode", False)
        self.hasDnD                = model_info.get("hasDnD", False)
        self.hasBatteryLevel       = model_info.get("hasBatteryLevel", False)

    def set_address(self, address):
        self.address = address

    def get_address(self):
        return self.address

    def get_model(self):
        return self.model

    def reset(self):
        self.address = ""
        self.name = ""
        self.shortName = ""
        self.model = WATCH_MODEL.UNKNOWN


watch_info = WatchInfo()
