from enum import Enum


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
    UNKNOWN = 10


class WatchInfo:
    def __init__(self):
        self.name = ""
        self.shortName = ""
        self.address = ""
        self.model = WATCH_MODEL.UNKNOWN
        self.worldCitiesCount = 2
        self.dstCount = 3
        self.alarmCount = 5
        self.hasAutoLight = False
        self.hasReminders = False
        self.shortLightDuration = ""
        self.longLightDuration = ""
        self.weekLanguageSupported = True
        self.worldCities: True
        self.temperature: True
        self.batteryLevelLowerLimit: 15
        self.batteryLevelUpperLimit: 20

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
                "model": WATCH_MODEL.GPR,
                "worldCitiesCount": 2,
                "dstCount": 1,
                "alarmCount": 5,
                "hasAutoLight": True,
                "hasReminders": False,
                "shortLightDuration": "1.5s",
                "longLightDuration": "3s",
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

        self.model_map = {model["model"]: model for model in self.models}

    def set_name_and_model(self, name):
        self.name = name

        parts = self.name.split(" ")
        if len(parts) > 1:
            self.shortName = parts[1]

        # *** Order matters. Start with the longest shortName first. ***
        if self.shortName.startswith("MSG"):
            self.model = WATCH_MODEL.MSG
        elif self.shortName.startswith("GPR"):
            self.model = WATCH_MODEL.GPR
        elif self.shortName.startswith("GST"):
            self.model = WATCH_MODEL.GST
        elif self.shortName.startswith("GBD"):
            self.model = WATCH_MODEL.GBD
        elif self.shortName.startswith("GMW"):
            self.model = WATCH_MODEL.GMW
        elif self.shortName.startswith("DW"):
            self.model = WATCH_MODEL.DW
        elif self.shortName.startswith("GA"):
            self.model = WATCH_MODEL.GA
        elif self.shortName.startswith("GB"):
            self.model = WATCH_MODEL.GB
        elif self.shortName.startswith("GM"):
            self.model = WATCH_MODEL.GM
        elif self.shortName.startswith("GW"):
            self.model = WATCH_MODEL.GW
        else:
            self.model = WATCH_MODEL.UNKNOWN

        model_info = self.model_map.get(self.model)
        if model_info:
            self.hasReminders = model_info["hasReminders"]
            self.hasAutoLight = model_info["hasAutoLight"]
            self.alarmCount = model_info["alarmCount"]
            self.worldCitiesCount = model_info["worldCitiesCount"]
            self.dstCount = model_info["dstCount"]
            self.shortLightDuration = model_info["shortLightDuration"]
            self.longLightDuration = model_info["longLightDuration"]
            self.weekLanguageSupported = model_info.get("weekLanguageSupported", True)
            self.worldCities = model_info.get("worldCities", True)
            self.temperature = model_info.get("temperature", True)
            self.batteryLevelLowerLimit = model_info.get("batteryLevelLowerLimit", 15)
            self.batteryLevelUpperLimit = model_info.get("batteryLevelUpperLimit", 20)

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
