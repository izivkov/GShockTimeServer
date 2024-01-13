import asyncio
import logging
import json
import time

from data_watcher import data_watcher
import message_dispatcher
from utils import (
    to_ascii_string,
    to_hex_string,
    to_int_array,
    to_compact_string,
    clean_str,
)
from result_queue import result_queue, KeyedResult
from casio_watch import WatchButton, DtsState
from alarms import alarms_inst
from event import Event
from watch_info import watch_info


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
        return await self._get_pressed_button("10")

    async def _get_pressed_button(self, key: str) -> WatchButton:
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def button_pressed_callback(keyed_data):
            """
            RIGHT BUTTON: 0x10 17 62 07 38 85 CD 7F ->04<- 03 0F FF FF FF FF 24 00 00 00
            LEFT BUTTON:  0x10 17 62 07 38 85 CD 7F ->01<- 03 0F FF FF FF FF 24 00 00 00
            RESET:        0x10 17 62 16 05 85 dd 7f ->00<- 03 0f ff ff ff ff 24 00 00 00 // after watch reset
            AUTO-TIME:    0x10 17 62 16 05 85 dd 7f ->03<- 03 0f ff ff ff ff 24 00 00 00 // no button pressed
            """

            result_value = keyed_data.get("value")
            result_key = keyed_data.get("key")

            ret = WatchButton.INVALID

            if (
                result_key == "10"
                and result_value != ""
                and len(to_int_array(result_value)) >= 19
            ):
                ble_int_arr = to_int_array(result_value)
                button_indicator = ble_int_arr[8]
                ret = (
                    WatchButton.LOWER_LEFT
                    if (button_indicator == 0 or button_indicator == 1)
                    else WatchButton.LOWER_RIGHT
                    if button_indicator == 4
                    else WatchButton.NO_BUTTON
                    if button_indicator == 3
                    else WatchButton.INVALID
                )

                res = result_queue.dequeue("10")
                res.set_result(ret)

        self.subscribe("BUTTON_PRESSED", button_pressed_callback)

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

    async def set_time(self, current_time=time.time()):
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

        # if watch_info.model == watch_info.model.B2100:
        await self.initialize_for_setting_time()
        # else:
        #     await self.initialize_for_setting_time()

        await self._set_time(current_time)

    async def _set_time(self, current_time):
        await message_dispatcher.TimeIO.request(self.connection, current_time)

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
        return await result

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

    async def get_time_adjustment(self):
        """Determine if auto-tame adjustment is set or not

        Parameters
        ----------
        None

        Returns
        -------
        is_time_adjustement_set: Boolean, True if time-adjustement is set.
        """
        key = "11"
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def get_time_adjustment(keyed_data):
            value = keyed_data.get("value")
            key = keyed_data.get("key")
            if key != "11":
                return

            res = result_queue.dequeue(key)
            time_adjustment = value.get("timeAdjustment", False)
            res.set_result(time_adjustment)

        self.subscribe("TIME_ADJUSTMENT", get_time_adjustment)
        return await result

    async def set_time_adjustment(self, settings):
        """Sets auto-tame adjustment for the watch

        Parameters
        ----------
        settings: Settings

        Returns
        -------
        None
        """
        await self.connection.sendMessage(
            """{"action": "SET_TIME_ADJUSTMENT", "value": \""""
            + str(settings.timeAdjustment)
            + """\" }"""
        )

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
        key = "13"
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def _get_settings(keyed_data):
            value = keyed_data.get("value")
            key = keyed_data.get("key")

            settings = json.loads(value)
            res = result_queue.dequeue(key)
            res.set_result(settings)

        self.subscribe("SETTINGS", _get_settings)
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

    async def get_event_from_watch(self, eventNumber: int):
        """Gets a single event (reminder) from the watch.

        Parameters
        ----------
        event_number: Integer, The index of the event 1..5

        Returns
        -------
        event: `Event`
        """
        await self.connection.request("30{}".format(eventNumber))  # reminder title
        await self.connection.request("31{}".format(eventNumber))  # reminder time

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult("310{}".format(eventNumber), result))

        def get_reminders(keyed_data):
            value = keyed_data.get("value")
            key = keyed_data.get("key")

            for obj_key in value:
                if obj_key == "title":
                    self.title = value[obj_key]

                elif obj_key == "time":
                    json_obj = json.loads("{}")
                    json_obj["title"] = self.title
                    json_obj["time"] = value.get("time")
                    event_obj = Event()
                    event = event_obj.create_event(json_obj)

                    res = result_queue.dequeue(key)
                    res.set_result(event)

        self.subscribe("REMINDERS", get_reminders)
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
                event_json = json.loads(json.dumps(event.__dict__))
                events_json.append(event_json)

            return events_json

        def get_selected_events(events: list):
            selected_events = [event for event in events if event.selected]
            return to_json(selected_events)

        selected = get_selected_events(events)

        await self.connection.sendMessage(
            """{{\"action\": \"SET_REMINDERS\", \"value\": {}}}""".format(
                json.dumps(selected)
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
        key = "22"
        await self.connection.request(key)

        def set_app_info(data: str):
            # App info:
            # This is needed to re-enable button D (Lower-right) after the watch has been reset or BLE has been cleared.
            # It is a hard-coded value, which is what the official app does as well.

            # If watch was reset, the app info will come as:
            # 0x22 FF FF FF FF FF FF FF FF FF FF 00
            # In this case, set it to the hardcoded value bellow, so 'D' button will
            # work again.
            app_info_compact_str = to_compact_string(data)
            if app_info_compact_str == "22FFFFFFFFFFFFFFFFFFFF00":
                self.connection.write(0xE, "223488F4E5D5AFC829E06D02")

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def subscribe_casio_app_information(keyed_data):
            data = keyed_data.get("value")
            key = keyed_data.get("key")

            set_app_info(data)
            res = result_queue.dequeue(key)
            res.set_result("")

        self.subscribe("CASIO_APP_INFORMATION", subscribe_casio_app_information)
        return await result

    def subscribe(self, subject_name, on_next) -> None:
        data_watcher.add_subject(subject_name)
        data_watcher.subscribe("GshockAPI", subject_name, on_next)
