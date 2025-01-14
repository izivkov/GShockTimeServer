import os
import logging
import time

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime, timedelta


casio_tz = {
 "UTC-12"               : {"A":0x39, "B":0x01, "OFF":0xD0, "DOFF":0x04, "DST":0x00, "NAME":b"BAKER ISLAND"},
 "Pacific/Pago_Pago"    : {"A":0xD7, "B":0x00, "OFF":0xD4, "DOFF":0x04, "DST":0x00, "NAME":b"PAGO PAGO"},
 "Pacific/Honolulu"     : {"A":0x7B, "B":0x00, "OFF":0xD8, "DOFF":0x04, "DST":0x00, "NAME":b"HONOLULU"},
 "Pacific/Marquesas"    : {"A":0x3A, "B":0x01, "OFF":0xDA, "DOFF":0x04, "DST":0x00, "NAME":b"MARQUESAS ISLANDS"},
 "America/Anchorage"    : {"A":0x0C, "B":0x00, "OFF":0xDC, "DOFF":0x04, "DST":0x01, "NAME":b"ANCHORAGE"},
 "America/Los_Angeles"  : {"A":0xA1, "B":0x00, "OFF":0xE0, "DOFF":0x04, "DST":0x01, "NAME":b"LOS ANGELES"},
 "America/Denver"       : {"A":0x54, "B":0x00, "OFF":0xE4, "DOFF":0x04, "DST":0x01, "NAME":b"DENVER"},
 "America/Chicago"      : {"A":0x42, "B":0x00, "OFF":0xE8, "DOFF":0x04, "DST":0x01, "NAME":b"CHICAGO"},
 "America/New_York"     : {"A":0xCA, "B":0x00, "OFF":0xEC, "DOFF":0x04, "DST":0x01, "NAME":b"NEW YORK"},
 "America/Halifax"      : {"A":0x71, "B":0x00, "OFF":0xF0, "DOFF":0x04, "DST":0x01, "NAME":b"HALIFAX"},
 "America/St_Johns"     : {"A":0x0C, "B":0x01, "OFF":0xF2, "DOFF":0x04, "DST":0x01, "NAME":b"ST.JOHN'S"},
 "America/Sao_Paulo"    : {"A":0xF1, "B":0x00, "OFF":0xF4, "DOFF":0x04, "DST":0x00, "NAME":b"RIO DE JANEIRO"},
 "America/Noronha"      : {"A":0x62, "B":0x00, "OFF":0xF8, "DOFF":0x04, "DST":0x00, "NAME":b"F.DE NORONHA"},
 "Atlantic/Cape_Verde"  : {"A":0xE9, "B":0x00, "OFF":0xFC, "DOFF":0x04, "DST":0x00, "NAME":b"PRAIA"},
 "UTC"                  : {"A":0x00, "B":0x00, "OFF":0x00, "DOFF":0x00, "DST":0x00, "NAME":b"UTC"},
 "Europe/London"        : {"A":0xA0, "B":0x00, "OFF":0x00, "DOFF":0x04, "DST":0x02, "NAME":b"LONDON"},
 "Europe/Paris"         : {"A":0xDC, "B":0x00, "OFF":0x04, "DOFF":0x04, "DST":0x02, "NAME":b"PARIS"},
 "Europe/Athens"        : {"A":0x13, "B":0x00, "OFF":0x08, "DOFF":0x04, "DST":0x02, "NAME":b"ATHENS"},
 "Asia/Riyadh"          : {"A":0x85, "B":0x00, "OFF":0x0C, "DOFF":0x04, "DST":0x00, "NAME":b"JEDDAH"},
 "Asia/Tehran"          : {"A":0x16, "B":0x01, "OFF":0x0E, "DOFF":0x04, "DST":0x2B, "NAME":b"TEHRAN"},
 "Asia/Dubai"           : {"A":0x5B, "B":0x00, "OFF":0x10, "DOFF":0x04, "DST":0x00, "NAME":b"DUBAI"},
 "Asia/Kabul"           : {"A":0x88, "B":0x00, "OFF":0x12, "DOFF":0x04, "DST":0x00, "NAME":b"KABUL"},
 "Asia/Karachi"         : {"A":0x8B, "B":0x00, "OFF":0x14, "DOFF":0x04, "DST":0x00, "NAME":b"KARACHI"},
 "Asia/Kolkata"         : {"A":0x52, "B":0x00, "OFF":0x16, "DOFF":0x04, "DST":0x00, "NAME":b"DELHI"},
 "Asia/Kathmandu"       : {"A":0x8C, "B":0x00, "OFF":0x17, "DOFF":0x04, "DST":0x00, "NAME":b"KATHMANDU"},
 "Asia/Dhaka"           : {"A":0x56, "B":0x00, "OFF":0x18, "DOFF":0x04, "DST":0x00, "NAME":b"DHAKA"},
 "Asia/Yangon"          : {"A":0x2F, "B":0x01, "OFF":0x1A, "DOFF":0x04, "DST":0x00, "NAME":b"YANGON"},
 "Asia/Bangkok"         : {"A":0x1C, "B":0x00, "OFF":0x1C, "DOFF":0x04, "DST":0x00, "NAME":b"BANGKOK"},
 "Asia/Hong_Kong"       : {"A":0x7A, "B":0x00, "OFF":0x20, "DOFF":0x04, "DST":0x00, "NAME":b"HONG KONG"},
 "Asia/Pyongyang"       : {"A":0xEA, "B":0x00, "OFF":0x24, "DOFF":0x04, "DST":0x00, "NAME":b"PYONGYANG"},
 "Australia/Eucla"      : {"A":0x36, "B":0x01, "OFF":0x23, "DOFF":0x04, "DST":0x00, "NAME":b"EUCLA"},
 "Asia/Tokyo"           : {"A":0x19, "B":0x01, "OFF":0x24, "DOFF":0x04, "DST":0x00, "NAME":b"TOKYO"},
 "Australia/Adelaide"   : {"A":0x05, "B":0x00, "OFF":0x26, "DOFF":0x04, "DST":0x04, "NAME":b"ADELAIDE"},
 "Australia/Sydney"     : {"A":0x0F, "B":0x01, "OFF":0x28, "DOFF":0x04, "DST":0x04, "NAME":b"SYDNEY"},
 "Australia/Lord_Howe"  : {"A":0x37, "B":0x01, "OFF":0x2A, "DOFF":0x02, "DST":0x12, "NAME":b"LORD HOWE ISLAND"},
 "Pacific/Noumea"       : {"A":0xCD, "B":0x00, "OFF":0x2C, "DOFF":0x04, "DST":0x00, "NAME":b"NOUMEA"},
 "Pacific/Auckland"     : {"A":0x2B, "B":0x01, "OFF":0x30, "DOFF":0x04, "DST":0x05, "NAME":b"WELLINGTON"},
 "Pacific/Chatham"      : {"A":0x3F, "B":0x00, "OFF":0x33, "DOFF":0x04, "DST":0x17, "NAME":b"CHATHAM ISLANDS"},
 "Pacific/Tongatapu"    : {"A":0xD0, "B":0x00, "OFF":0x34, "DOFF":0x04, "DST":0x00, "NAME":b"NUKUALOFA"},
 "Pacific/Kiritimati"   : {"A":0x93, "B":0x00, "OFF":0x38, "DOFF":0x04, "DST":0x00, "NAME":b"KIRITIMATI"},
 "Asia/Jerusalem"       : {"A":0x86, "B":0x00, "OFF":0x08, "DOFF":0x04, "DST":0x2A, "NAME":b"JERUSALEM"},
 "Africa/Casablanca"    : {"A":0x3A, "B":0x00, "OFF":0x00, "DOFF":0x04, "DST":0x0F, "NAME":b"CASABLANCA"},
 "Asia/Beirut"          : {"A":0x22, "B":0x00, "OFF":0x08, "DOFF":0x04, "DST":0x0C, "NAME":b"BEIRUT"},
 "Pacific/Norfolk"      : {"A":0x38, "B":0x01, "OFF":0x2C, "DOFF":0x04, "DST":0x04, "NAME":b"NORFOLK ISLAND"},
 "Pacific/Easter"       : {"A":0x5E, "B":0x00, "OFF":0xE8, "DOFF":0x04, "DST":0x1C, "NAME":b"EASTER ISLAND"},
 "America/Havana"       : {"A":0x75, "B":0x00, "OFF":0xEC, "DOFF":0x04, "DST":0x15, "NAME":b"HAVANA"},
 "America/Santiago"     : {"A":0x02, "B":0x01, "OFF":0xF0, "DOFF":0x04, "DST":0x1B, "NAME":b"SANTIAGO"},
 "America/Santo_Domingo": {"A":0x03, "B":0x01, "OFF":0xF0, "DOFF":0x04, "DST":0x00, "NAME":b"SANTO DOMINGO"},
 "America/Asuncion"     : {"A":0x12, "B":0x00, "OFF":0xF0, "DOFF":0x04, "DST":0x09, "NAME":b"ASUNCION"},
 "Atlantic/Azores"      : {"A":0xE4, "B":0x00, "OFF":0xFC, "DOFF":0x04, "DST":0x02, "NAME":b"PONTA DELGADA"},
}


def tz_from_name (name : str) :
    if name in casio_tz :
        return casio_tz[name]

    try:
        tz = ZoneInfo(name)

        name = name.split("/")[-1].replace("_", " ").upper()

        offset = int(tz.utcoffset(datetime(2025,1,1)).seconds/900)
        dst_offset = int(tz.dst(datetime(2025,8,1)).seconds/900)

        logging.info(f"offset for {name} : {offset}, dst : {dst_offset}")

        ctz = {"A" : 0,
               "B" : 0,
               "OFF" : offset if offset <= 48 else 160 + offset,
               "DOFF" : dst_offset,
               "DST": 0x02 if dst_offset > 0 else 0,
               "NAME" : name.encode("UTF-8")}

        return ctz

    except ZoneInfoNotFoundError:
        return casio_tz["UTC"]

    return casio_tz["UTC"]

def casio_city_name(prefix, name) :
    return prefix + name + bytearray(18 - len(name))

class SysTZ:
    def __init__(self):
        self.refresh()

    def refresh (self) :
        with os.popen("realpath /etc/localtime") as s:
            t = s.read()

        self.name = t[len("/etc/zoneinfo/"):-1]
        self.zoneinfo = ZoneInfo(self.name)
        logging.info(f"We are in {self.name} TZ")
        self.casiotz = tz_from_name(self.name)
        os.environ['TZ'] = self.name
        time.tzset() # now time.time() will give the good timestamp

    def get_name (self) :
        return self.casiotz["NAME"]

sys_tz = SysTZ()
