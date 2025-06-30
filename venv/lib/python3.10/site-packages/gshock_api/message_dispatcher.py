import sys
import asyncio
import json
from typing import Any
from gshock_api.logger import logger
from gshock_api.casio_constants import CasioConstants
from gshock_api.iolib.app_info_io import AppInfoIO
from gshock_api.iolib.dst_watch_state_io import DstWatchStateIO
from gshock_api.iolib.world_cities_io import WorldCitiesIO
from gshock_api.iolib.dst_for_world_cities_io import DstForWorldCitiesIO

from gshock_api.iolib.time_io import TimeIO
from gshock_api.iolib.timer_io import TimerIO
from gshock_api.iolib.watch_name_io import WatchNameIO
from gshock_api.iolib.alarms_io import AlarmsIO
from gshock_api.iolib.events_io import EventsIO
from gshock_api.iolib.settings_io import SettingsIO
from gshock_api.iolib.time_adjustement_io import TimeAdjustmentIO
from gshock_api.iolib.watch_condition_io import WatchConditionIO
from gshock_api.iolib.error_io import ErrorIO
from gshock_api.iolib.unknown_io import UnknownIO
from gshock_api.iolib.button_pressed_io import ButtonPressedIO

CHARACTERISTICS = CasioConstants.CHARACTERISTICS

class MessageDispatcher:
    watch_senders = {
        "GET_ALARMS": AlarmsIO.send_to_watch,
        "SET_ALARMS": AlarmsIO.send_to_watch_set,
        "SET_REMINDERS": EventsIO.send_to_watch_set,
        "GET_SETTINGS": SettingsIO.send_to_watch,
        "SET_SETTINGS": SettingsIO.send_to_watch_set,
        "GET_TIME_ADJUSTMENT": TimeAdjustmentIO.send_to_watch,
        "SET_TIME_ADJUSTMENT": TimeAdjustmentIO.send_to_watch_set,
        "GET_TIMER": TimerIO.send_to_watch,
        "SET_TIMER": TimerIO.send_to_watch_set,
        "SET_TIME": TimeIO.send_to_watch_set,
    }

    data_received_messages = {
        CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]: AlarmsIO.on_received,
        CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]: AlarmsIO.on_received,
        CHARACTERISTICS["CASIO_TIMER"]: TimerIO.on_received,
        CHARACTERISTICS["CASIO_WATCH_NAME"]: WatchNameIO.on_received,
        CHARACTERISTICS["CASIO_DST_SETTING"]: DstForWorldCitiesIO.on_received,
        CHARACTERISTICS["CASIO_REMINDER_TIME"]: EventsIO.on_received,
        CHARACTERISTICS["CASIO_REMINDER_TITLE"]: EventsIO.on_received_title,
        CHARACTERISTICS["CASIO_WORLD_CITIES"]: WorldCitiesIO.on_received,
        CHARACTERISTICS["CASIO_DST_WATCH_STATE"]: DstWatchStateIO.on_received,
        CHARACTERISTICS["CASIO_WATCH_CONDITION"]: WatchConditionIO.on_received,
        CHARACTERISTICS["CASIO_APP_INFORMATION"]: AppInfoIO.on_received,
        CHARACTERISTICS["CASIO_BLE_FEATURES"]: ButtonPressedIO.on_received,
        CHARACTERISTICS["CASIO_SETTING_FOR_BASIC"]: SettingsIO.on_received,
        CHARACTERISTICS["CASIO_SETTING_FOR_BLE"]: TimeAdjustmentIO.on_received,
        CHARACTERISTICS["ERROR"]: ErrorIO.on_received,
        CHARACTERISTICS["UNKNOWN"]: UnknownIO.on_received,

        #  ECB-30
        CHARACTERISTICS["CMD_SET_TIMEMODE"]: UnknownIO.on_received,
        CHARACTERISTICS["FIND_PHONE"]: UnknownIO.on_received,
    }

    @staticmethod
    async def send_to_watch(message):
        json_message = json.loads(message)
        action = json_message.get("action")
        await MessageDispatcher.watch_senders[action](message)

    @staticmethod
    def on_received(data):
        key = data[0]
        if key not in MessageDispatcher.data_received_messages:
            logger.info(f"Unknown key: {key}")
        else:
            MessageDispatcher.data_received_messages[key](data)

# Usage example
if __name__ == "__main__":
    # Simulated messages
    sample_message = {"action": "GET_SETTINGS"}
    sample_data = "1,2,3,4,5"

    # Simulated message dispatching
    MessageDispatcher.send_to_watch(sample_message)
    MessageDispatcher.on_received(sample_data)
