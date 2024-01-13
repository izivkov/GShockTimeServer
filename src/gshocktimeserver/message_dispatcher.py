import sys
import asyncio
import json
from typing import Any
import connection
from casio_constants import CasioConstants
from iolib.dst_watch_state_io import DstWatchStateIO
from iolib.world_cities_io import WorldCitiesIO
from iolib.dst_for_world_cities_io import DstForWorldCitiesIO

from iolib.time_io import TimeIO
from iolib.timer_io import TimerIO
from iolib.watch_name_io import WatchNameIO
from iolib.alarms_io import AlarmsIO

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class EventsIO:
    @staticmethod
    def send_to_watch_set(message):
        print(f"EventsIO sendToWatchSet: {message}")

    @staticmethod
    def on_received(message):
        print(f"EventsIO onReceived: {message}")

    @staticmethod
    def on_received_title(message):
        print(f"EventsIO onReceivedTitle: {message}")


class SettingsIO:
    @staticmethod
    def send_to_watch(message):
        print(f"SettingsIO sendToWatch: {message}")

    @staticmethod
    def send_to_watch_set(message):
        print(f"SettingsIO sendToWatchSet: {message}")

    @staticmethod
    def on_received(message):
        print(f"SettingsIO onReceived: {message}")


class TimeAdjustmentIO:
    @staticmethod
    def send_to_watch(message):
        print(f"TimeAdjustmentIO sendToWatch: {message}")

    @staticmethod
    def send_to_watch_set(message):
        print(f"TimeAdjustmentIO sendToWatchSet: {message}")

    @staticmethod
    def on_received(message):
        print(f"TimeAdjustmentIO onReceived: {message}")


class WatchConditionIO:
    @staticmethod
    def on_received(message):
        print(f"WatchConditionIO onReceived: {message}")


class AppInfoIO:
    @staticmethod
    def on_received(message):
        print(f"AppInfoIO onReceived: {message}")


class ButtonPressedIO:
    @staticmethod
    def on_received(message):
        print(f"ButtonPressedIO onReceived: {message}")


class ErrorIO:
    @staticmethod
    def on_received(message):
        print(f"ErrorIO onReceived: {message}")


class UnknownIO:
    @staticmethod
    def on_received(message):
        print(f"UnknownIO onReceived: {message}")


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
            print(f"Unknown key: {key}")
        else:
            print(f"Found key: {MessageDispatcher.data_received_messages[key]}")
            MessageDispatcher.data_received_messages[key](data)


# Usage example
if __name__ == "__main__":
    # Simulated messages
    sample_message = {"action": "GET_SETTINGS"}
    sample_data = "1,2,3,4,5"

    # Simulated message dispatching
    MessageDispatcher.send_to_watch(sample_message)
    MessageDispatcher.on_received(sample_data)
