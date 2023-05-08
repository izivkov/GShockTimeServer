import json
import logging
import numpy as np
from casio_constants import CasioConstants
from utils import to_int_array, to_compact_string, to_hex_string

logger = logging.getLogger(__name__)

HOURLY_CHIME_MASK = 0b10000000
ENABLED_MASK = 0b01000000
ALARM_CONSTANT_VALUE = 0x40

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class Alarm:
    def __init__(self, hour, minute, enabled, has_hourly_chime):
        self.hour = hour
        self.minute = minute
        self.enabled = enabled
        self.has_hourly_chime = has_hourly_chime


class Alarms:
    alarms = []

    def clear(self):
        self.alarms.clear()

    def add_alarms(self, alarm_json_str_arr):
        for alarm_json_str in alarm_json_str_arr:
            alarm = json.loads(alarm_json_str)
            self.alarms.append(alarm)

    def from_json_alarm_first_alarm(self, alarm):
        return self.create_first_alarm(alarm)

    def create_first_alarm(self, alarm):
        flag = 0
        if alarm.get("enabled"):
            flag = flag | ENABLED_MASK
        if alarm.get("hasHourlyChime"):
            flag = flag | HOURLY_CHIME_MASK

        return bytearray(
            [
                CHARACTERISTICS["CASIO_SETTING_FOR_ALM"],
                flag,
                ALARM_CONSTANT_VALUE,
                alarm.get("hour"),
                alarm.get("minute"),
            ]
        )

    def from_json_alarm_secondary_alarms(self, alarms_json):
        if len(alarms_json) < 2:
            return []
        alarms = self.alarms[1:]
        return self.create_secondary_alarm(alarms)

    def create_secondary_alarm(self, alarms):
        all_alarms = bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]])

        for alarm in alarms:
            flag = 0
            if alarm.get("enabled"):
                flag = flag | ENABLED_MASK
            if alarm.get("hasHourlyChime"):
                flag = flag | HOURLY_CHIME_MASK

            all_alarms += bytearray(
                [flag, ALARM_CONSTANT_VALUE, alarm.get("hour"), alarm.get("minute")]
            )

        return all_alarms


alarms_inst = Alarms()


class AlarmDecoder:
    def to_json(self, command: str):
        json_response = {}
        int_array = to_int_array(command)
        alarms = []

        if int_array[0] == CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]:
            int_array.pop(0)
            alarms.append(self.create_json_alarm(int_array))
            json_response["ALARMS"] = alarms
        elif int_array[0] == CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]:
            int_array.pop(0)
            for item in np.array_split(int_array, 4):
                alarms.append(self.create_json_alarm(item))
            json_response["ALARMS"] = alarms
        else:
            logger.info("Unhandled Command {}".format(command))

        return json_response

    def create_json_alarm(self, int_array):
        alarm = Alarm(
            int_array[2],
            int_array[3],
            int_array[0] & ENABLED_MASK != 0,
            int_array[0] & HOURLY_CHIME_MASK != 0,
        )
        return self.to_json_new_alarm(alarm)

    def to_json_new_alarm(self, alarm):
        return json.dumps(
            {
                "enabled": bool(alarm.enabled),
                "hasHourlyChime": bool(alarm.has_hourly_chime),
                "hour": int(alarm.hour),
                "minute": int(alarm.minute),
            }
        )


alarm_decoder = AlarmDecoder()
