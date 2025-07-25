import logging
import json
import time

from gshock_api.iolib.dst_watch_state_io import DtsState
from gshock_api.iolib.button_pressed_io import WatchButton
from gshock_api.iolib.app_notification_io import AppNotificationIO

from gshock_api import message_dispatcher
from gshock_api.utils import (
    to_hex_string,
    to_compact_string,
)
from gshock_api.alarms import alarms_inst
from gshock_api.event import Event
from gshock_api.watch_info import watch_info

class GshockAPI:
    """
    This class contains all the API functions. This should the the main interface to the
    library.

    Here is how to use it:

        api = GshockAPI(connection)

        pressed_button = await api.getPressedButton()
        watch_name = await api.getWatchName()
        await api.set_time()
        ...
    """

    logger = logging.getLogger("GshockAPI")

    def __init__(self, connection):
        self.connection = connection

    async def get_watch_name(self):
        """Get the name of the watch.

        Parameters
        ----------
        none

        Returns
        -------
        name : String, i.e: "GW-B5600"
        """
        return await self._get_watch_name()

    async def _get_watch_name(self):
        result = await message_dispatcher.WatchNameIO.request(self.connection)
        return await result

    async def get_pressed_button(self) -> WatchButton:
        """This function tells us which button was pressed on the watch to
        initiate the connection. Remember, the connection between the phone and the
        watch can only be initiated from the <b>watch</b>.

        The return values are interpreted as follows:

        - `LOWER_LEFT` - this connection is initiated by a long-press of the lower-left
            button on the watch.The app receiving this type of connection can now send and
            receive commands to the watch.

        - `LOWER_RIGHT` - this connection is initiated by a short-press of the lower-right button,
            which is usually used to set time. But the app can use this signal to perform other
            arbitrary functions. Therefore, this button is also referred as `ACTION BUTTON`.
            The connection will automatically disconnect in about 20 seconds.

        - `NO_BUTTON` - this connection is initiated automatically, periodically
            from the watch, without user input. It will automatically disconnect in about 20 seconds.

        Parameters
        ----------
        none

        Returns
        -------
        button: WATCH_BUTTON
        """
        result = await message_dispatcher.ButtonPressedIO.request(self.connection)
        return await result

    async def get_world_cities(self, cityNumber: int):
        """Get the name for a particular World City set on the watch. There are 6 world cities that can be stored.

        Parameters
        ----------
        city_number: Integer (0..5)

        Returns
        -------
        name : String, The name of the requested World City as a String.
        """
        city = await self._get_world_cities(cityNumber)
        return city

    async def _get_world_cities(self, key: str):
        result = await message_dispatcher.WorldCitiesIO.request(self.connection, key)
        return await result

    async def get_dst_for_world_cities(self, cityNumber: int) -> str:
        """Get the **Daylight Saving Time** for a particular World City set on the watch.
            There are 6 world cities that can be stored.

        Parameters
        ----------
        cityNumber: Integer, index of the world city (0..5)

        Returns
        -------
        name : String, Daylight Saving Time state of the requested World City as a String.
        """
        return await self._get_dst_for_world_cities(cityNumber)

    async def _get_dst_for_world_cities(self, key: str) -> str:
        result = await message_dispatcher.DstForWorldCitiesIO.request(
            self.connection, key
        )
        return await result

    async def get_dst_watch_state(self, state: DtsState) -> str:
        """Get the DST state of the watch.

        Parameters
        ----------
        None

        Returns
        -------
        dst: String, the Daylight Saving Time state of the watch as a String.
        """
        return await self._get_dst_watch_state(state)

    async def _get_dst_watch_state(self, state: DtsState) -> str:
        result = await message_dispatcher.DstWatchStateIO.request(
            self.connection, state
        )
        return await result

    async def initialize_for_setting_time(self):
        await self.read_write_dst_watch_states()
        await self.read_write_dst_for_world_cities()
        await self.read_write_world_cities()

    async def read_and_write(self, function, param):
        ret = await function(param)
        short_str = to_compact_string(to_hex_string(ret))
        await self.connection.write(0xE, short_str)

    async def read_write_dst_watch_states(self):
        array_of_dst_watch_state = [
            {"function": self.get_dst_watch_state, "state": DtsState.ZERO},
            {"function": self.get_dst_watch_state, "state": DtsState.TWO},
            {"function": self.get_dst_watch_state, "state": DtsState.FOUR},
        ]

        for item in array_of_dst_watch_state[: watch_info.dstCount]:
            await self.read_and_write(item["function"], item["state"])

    async def send_app_notification (self, hex_str):
        await self.connection.write(0xD, hex_str)

    async def read_write_dst_for_world_cities(self):
        array_of_get_dst_for_world_cities = [
            {"function": self.get_dst_for_world_cities, "city_number": 0},
            {"function": self.get_dst_for_world_cities, "city_number": 1},
            {"function": self.get_dst_for_world_cities, "city_number": 2},
            {"function": self.get_dst_for_world_cities, "city_number": 3},
            {"function": self.get_dst_for_world_cities, "city_number": 4},
            {"function": self.get_dst_for_world_cities, "city_number": 5},
        ]

        for item in array_of_get_dst_for_world_cities[: watch_info.worldCitiesCount]:
            await self.read_and_write(item["function"], item["city_number"])

    async def read_write_world_cities(self):
        array_of_world_cities = [
            {"function": self.get_world_cities, "city_number": 0},
            {"function": self.get_world_cities, "city_number": 1},
            {"function": self.get_world_cities, "city_number": 2},
            {"function": self.get_world_cities, "city_number": 3},
            {"function": self.get_world_cities, "city_number": 4},
            {"function": self.get_world_cities, "city_number": 5},
        ]

        for item in array_of_world_cities[: watch_info.worldCitiesCount]:
            await self.read_and_write(item["function"], item["city_number"])

    async def set_time(self, current_time=None, offset = 0):
        """Sets the current time on the watch from the time on the phone. In addition, it can optionally set the Home Time
        to the current time zone. If timezone changes during travel, the watch will automatically be set to the
        correct time and timezone after running this function.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        # if current_time == None:
        #     current_time = time.time()

        await self.initialize_for_setting_time()
        await self._set_time(current_time, offset)
        current_time = None

    async def _set_time(self, current_time, offset = 0):
        await message_dispatcher.TimeIO.request(self.connection, current_time, offset)

    async def get_alarms(self):
        """Gets the current alarms from the watch. Up to 5 alarms are supported on the watch.

        Parameters
        ----------
        None

        Returns
        -------
        alarms: List of `Alarm`
        """
        alarms_inst.clear()
        await self._get_alarms()
        return alarms_inst.alarms

    async def _get_alarms(self):
        result = await message_dispatcher.AlarmsIO.request(self.connection)
        return result

    async def set_alarms(self, alarms):
        """Sets alarms to the watch. Up to 5 alarms are supported on the watch.

        Parameters
        ----------
        alarms: List of `Alarm`

        Returns
        -------
        None
        """
        if not alarms:
            self.logger.debug("Alarm model not initialised! Cannot set alarm")
            return

        alarms_str = json.dumps(alarms)
        set_action_cmd = '{{"action":"SET_ALARMS", "value":{} }}'.format(alarms_str)
        await self.connection.sendMessage(set_action_cmd)

    async def get_timer(self):
        """Get Timer value in seconds.

        Parameters
        ----------
        None

        Returns
        -------
        timer_value: Integer, the timer number in seconds as an Int. E.g.: 180 means the timer is set for 3 minutes.
        """
        return await self._get_timer()

    async def _get_timer(self):
        result = await message_dispatcher.TimerIO.request(self.connection)
        return await result

    async def set_timer(self, timerValue):
        """Set Timer value in seconds.

        Parameters
        ----------
        Timer number of seconds as an Int.  E.g.: 180 means the timer will be set for 3 minutes.

        Returns
        -------
        None
        """
        await self.connection.sendMessage(
            """{"action": "SET_TIMER", "value": """ + str(timerValue) + """ }"""
        )

    async def get_watch_condition(self):
        result = await message_dispatcher.WatchConditionIO.request(self.connection)
        return await result

    async def get_time_adjustment(self):
        """Determine if auto-tame adjustment is set or not

        Parameters
        ----------
        None

        Returns
        -------
        is_time_adjustement_set: Boolean, True if time-adjustement is set.
        """
        result = await message_dispatcher.TimeAdjustmentIO.request(self.connection)
        return await result

    async def set_time_adjustment(
        self, time_adjustement: bool, minutes_after_hour: int
    ):
        """Sets auto-tame adjustment for the watch

        Parameters
        ----------
        time_adjustement: bool, True if time-adjustement is set
        minutes_after_hour: int, minutes after hour

        Returns
        -------
        None
        """
        message = f"""{{"action": "SET_TIME_ADJUSTMENT", "timeAdjustment": "{time_adjustement}", "minutesAfterHour": "{minutes_after_hour}" }}"""
        await self.connection.sendMessage(message)

    async def get_basic_settings(self):
        """Get settings from the watch. Example:

        ```
        settings_local = await api.get_basic_settings()
        ```

        Parameters
        ----------
        None

        Returns
        -------
        settings: a list of `Settings`
        """

        result = await message_dispatcher.SettingsIO.request(self.connection)
        return await result

    async def set_settings(self, settings):
        """Set settings to the watch. Populate a [Settings] and call this function. Example:
        ```
        settings_local["button_tone"] = True
        settings_local["language"] = "Engish"
        settings_local["time_format"] = "12h"

        await api.set_settings(settings_local)

        ```

        Parameters
        ----------
        settings: a list of `Settings`

        Returns
        -------
        None
        """
        setting_json = json.dumps(settings)
        await self.connection.sendMessage(
            """{"action": "SET_SETTINGS", "value": """ + setting_json + """ }"""
        )

    async def get_reminders(self):
        """Gets the current reminders (events) from the watch. Up to 5 events are supported.

        Parameters
        ----------
        None

        Returns
        -------
        events: list of `Event`
        """
        reminders = []

        reminders.append(await self.get_event_from_watch(1))
        reminders.append(await self.get_event_from_watch(2))
        reminders.append(await self.get_event_from_watch(3))
        reminders.append(await self.get_event_from_watch(4))
        reminders.append(await self.get_event_from_watch(5))

        return reminders

    async def get_event_from_watch(self, event_number: int):
        """Gets a single event (reminder) from the watch.

        Parameters
        ----------
        event_number: Integer, The index of the event 1..5

        Returns
        -------
        event: `Event`
        """
        result = await message_dispatcher.EventsIO.request(
            self.connection, event_number
        )
        return await result

    async def set_reminders(self, events: list):
        """Sets events (reminders) to the watch. Up to 5 events are supported.

        Parameters
        ----------
        events: list of `Event`

        Returns
        -------
        None
        """
        if not events:
            return

        def to_json(events: list):
            events_json = json.loads("[]")
            for event in events:
                event_json = event  # json.loads(json.dumps(event.__dict__))
                events_json.append(event_json)

            return events_json

        def get_enabled_events(events: list):
            enabled_events = [event for event in events if event["time"]["enabled"]]
            return enabled_events  # to_json(enabled_events)

        enabled = get_enabled_events(events)

        await self.connection.sendMessage(
            """{{\"action\": \"SET_REMINDERS\", \"value\": {}}}""".format(
                json.dumps(enabled)
            )
        )

    async def get_app_info(self):
        """Gets and internally sets app info to the watch.
            This is needed to re-enable lower-right button after the watch has been reset or BLE has been cleared.
            Call this function after each time the connection has been established.

        Parameters
        ----------
        None

        Returns
        -------
        app_info: String
        """

        result = await message_dispatcher.AppInfoIO.request(self.connection)
        return await result

    async def send_app_notification (self, notification):
        encoded_buffer = AppNotificationIO.encode_notification_packet(notification)
        encrypted_buffer = AppNotificationIO.xor_encode_buffer(encoded_buffer)
        await self.connection.write(0xD, encrypted_buffer)

