import asyncio
import json
from typing import Any
from gshock_api.cancelable_result import CancelableResult
from gshock_api.settings import settings
from gshock_api.utils import to_compact_string, to_hex_string, to_int_array
from gshock_api.casio_constants import CasioConstants
from gshock_api.logger import logger

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class SettingsIO:
    result: CancelableResult = None
    connection = None

    @staticmethod
    async def request(connection):
        SettingsIO.connection = connection
        await connection.request("13")

        SettingsIO.result = CancelableResult()
        return SettingsIO.result.get_result()

    @staticmethod
    def send_to_watch(message):
        SettingsIO.connection.write(
            0x000C, bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_BASIC"]])
        )

    @staticmethod
    async def send_to_watch_set(message):
        def encode(settings):
            mask_24_hours = 0b00000001
            MASK_BUTTON_TONE_OFF = 0b00000010
            MASK_LIGHT_OFF = 0b00000100
            POWER_SAVING_MODE = 0b00010000

            arr = bytearray(12)
            arr[0] = CHARACTERISTICS["CASIO_SETTING_FOR_BASIC"]
            if settings.time_format == "24h":
                arr[1] = arr[1] | mask_24_hours
            if not settings.button_tone:
                arr[1] = arr[1] | MASK_BUTTON_TONE_OFF
            if not settings.auto_light:
                arr[1] = arr[1] | MASK_LIGHT_OFF
            if not settings.power_saving_mode:
                arr[1] = arr[1] | POWER_SAVING_MODE

            if settings.light_duration == "4s":
                arr[2] = 1
            if settings.date_format == "DD:MM":
                arr[4] = 1

            language_index = {
                "English": 0,
                "Spanish": 1,
                "French": 2,
                "German": 3,
                "Italian": 4,
                "Russian": 5,
            }
            arr[5] = language_index.get(settings.language, 0)

            return arr

        class DotDict(dict):
            def __getattr__(self, attr):
                if attr in self:
                    return self[attr]
                else:
                    raise AttributeError(f"'DotDict' object has no attribute '{attr}'")

            __setattr__ = dict.__setitem__
            __delattr__ = dict.__delitem__

        json_setting = json.loads(message).get("value")
        # dict_setting = json.load(json_setting)
        encoded_stiing = encode(DotDict(json_setting))
        setting_to_set = to_compact_string(to_hex_string(encoded_stiing))

        await SettingsIO.connection.write(0x000E, setting_to_set)

    @staticmethod
    def on_received(message):
        logger.info(f"SettingsIO onReceived: {message}")

        def create_json_settings(setting_string):
            mask_24_hours = 0b00000001
            MASK_BUTTON_TONE_OFF = 0b00000010
            MASK_LIGHT_OFF = 0b00000100
            POWER_SAVING_MODE = 0b00010000

            setting_array = to_int_array(setting_string)

            if setting_array[1] & mask_24_hours != 0:
                settings.time_format = "24h"
            else:
                settings.time_format = "12h"
            settings.button_tone = setting_array[1] & MASK_BUTTON_TONE_OFF == 0
            settings.auto_light = setting_array[1] & MASK_LIGHT_OFF == 0
            settings.power_saving_mode = setting_array[1] & POWER_SAVING_MODE == 0

            if setting_array[4] == 1:
                settings.date_format = "DD:MM"
            else:
                settings.date_format = "MM:DD"

            if setting_array[5] == 0:
                settings.language = "English"
            if setting_array[5] == 1:
                settings.language = "Spanish"
            if setting_array[5] == 2:
                settings.language = "French"
            if setting_array[5] == 3:
                settings.language = "German"
            if setting_array[5] == 4:
                settings.language = "Italian"
            if setting_array[5] == 5:
                settings.language = "Russian"

            if setting_array[2] == 1:
                settings.light_duration = "4s"
            else:
                settings.light_duration = "2s"

            return json.dumps(settings.__dict__)

        data = to_hex_string(message)
        json_data = json.loads(create_json_settings(data))
        SettingsIO.result.set_result(json_data)
