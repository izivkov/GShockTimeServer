import asyncio
import logging
import json
import time

from data_watcher import data_watcher
from utils import (
    to_ascii_string,
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
        return await self._get_watch_name("23")

    async def _get_watch_name(self, key):
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def on_data_received(keyed_data):
            _key = "23"

            result_value = keyed_data.get("value")
            result_key = keyed_data.get("key")

            if result_key == _key:
                result_str = clean_str(to_ascii_string(result_value, 1))
                res = result_queue.dequeue(_key)
                res.set_result(result_str)

        self.subscribe("CASIO_WATCH_NAME", lambda data: on_data_received(data))
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
        key = "1f0{}".format(cityNumber)
        city = await self._get_world_cities(key)
        return city

    async def _get_world_cities(self, key: str):
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def casio_world_cities_callback(keyed_data):
            value = keyed_data.get("value")
            key = keyed_data.get("key")

            res = result_queue.dequeue(key)
            res.set_result(value)

        def process_home_time(keyed_data):
            pass

        self.subscribe("CASIO_WORLD_CITIES", casio_world_cities_callback)
        # self.subscribe("HOME_TIME", process_home_time)
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
        key = "1e0{}".format(cityNumber)
        return await self._get_dst_for_world_cities(key)

    async def _get_dst_for_world_cities(self, key: str) -> str:
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def casio_dts_world_cities_callback(keyed_data):
            value = keyed_data.get("value")
            key = keyed_data.get("key")

            res = result_queue.dequeue(key)
            res.set_result(value)

        self.subscribe("CASIO_DST_SETTING", casio_dts_world_cities_callback)

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
        key = f"1d0{state.value}"
        return await self._get_dst_watch_state(key)

    async def _get_dst_watch_state(self, key: str) -> str:
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def handle_message(keyed_data):
            value = keyed_data.get("value")
            key = keyed_data.get("key")

            res = result_queue.dequeue(key)
            res.set_result(value)

        self.subscribe("CASIO_DST_WATCH_STATE", handle_message)

        return await result

    # async def reset_hand_to_12 (self):
    #     await self.connection.write(0xE, "1a0412000000")
    #     await self.connection.write(0xE, "1a0418000000")

    async def initialize_for_setting_time(self):
        # Before we can set time, we must read and write back these values.
        # Why? Not sure, ask Casio

        async def read_and_rite(function, param):
            ret = await function(param)
            short_str = to_compact_string(ret)
            await self.connection.write(0xE, short_str)

        await read_and_rite(self.get_dst_watch_state, DtsState.ZERO)
        await read_and_rite(self.get_dst_watch_state, DtsState.TWO)
        await read_and_rite(self.get_dst_watch_state, DtsState.FOUR)

        await read_and_rite(self.get_dst_for_world_cities, 0)
        await read_and_rite(self.get_dst_for_world_cities, 1)
        await read_and_rite(self.get_dst_for_world_cities, 2)
        await read_and_rite(self.get_dst_for_world_cities, 3)
        await read_and_rite(self.get_dst_for_world_cities, 4)
        await read_and_rite(self.get_dst_for_world_cities, 5)

        await read_and_rite(self.get_world_cities, 0)
        await read_and_rite(self.get_world_cities, 1)
        await read_and_rite(self.get_world_cities, 2)
        await read_and_rite(self.get_world_cities, 3)
        await read_and_rite(self.get_world_cities, 4)
        await read_and_rite(self.get_world_cities, 5)

    async def initialize_for_setting_time_b2100(self):
        # Before we can set time, we must read and write back these values.
        # Why? Not sure, ask Casio

        async def read_and_rite(function, param):
            ret = await function(param)
            short_str = to_compact_string(ret)
            await self.connection.write(0xE, short_str)

        await read_and_rite(self.get_dst_watch_state, DtsState.ZERO)
        await read_and_rite(self.get_dst_for_world_cities, 0)
        await read_and_rite(self.get_dst_for_world_cities, 1)

        await read_and_rite(self.get_world_cities, 0)
        await read_and_rite(self.get_world_cities, 1)

    async def set_time(self):
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

        if watch_info.model == watch_info.model.B2100:
            await self.initialize_for_setting_time_b2100()
        else:
            await self.initialize_for_setting_time()

        message = {
            "action": "SET_TIME",
            "value": "{}".format(round(time.time() * 1000)),
        }
        await self.connection.sendMessage(json.dumps(message))

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
        await self._get_alarms2()
        return alarms_inst.alarms

    async def _get_alarms(self):
        await self.connection.sendMessage("""{ "action": "GET_ALARMS"}""")
        key = "GET_ALARMS"

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def alarms_received(keyed_data):
            data = keyed_data.get("value")
            key = "GET_ALARMS"

            alarms_inst.add_alarms(data)

            res = result_queue.dequeue(key)
            res.set_result(data)

        self.subscribe("ALARMS", alarms_received)
        return await result

    async def _get_alarms2(self):
        await self.connection.sendMessage("""{ "action": "GET_ALARMS2"}""")
        key = "GET_ALARMS2"

        # Alarm.alarms.clear()

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def alarms_received2(keyed_data):
            data = keyed_data.get("value")
            key = "GET_ALARMS2"

            alarms_inst.add_alarms(data)

            res = result_queue.dequeue(key)
            res.set_result(data)

        self.subscribe("ALARMS2", alarms_received2)
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
        self.logger.debug("Returning from setAlarms")

    async def get_timer(self):
        """Get Timer value in seconds.

        Parameters
        ----------
        None

        Returns
        -------
        timer_value: Integer, the timer number in seconds as an Int. E.g.: 180 means the timer is set for 3 minutes.
        """
        return await self._get_timer("18")

    async def _get_timer(self, key):
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def decode_value(data: str) -> str:
            timer_int_array = to_int_array(data)

            hours = timer_int_array[1]
            minutes = timer_int_array[2]
            seconds = timer_int_array[3]

            in_seconds = hours * 3600 + minutes * 60 + seconds
            return in_seconds

        def get_timer(keyed_data):
            value = keyed_data.get("value")
            key = keyed_data.get("key")

            seconds = decode_value(value)
            res = result_queue.dequeue(key)
            res.set_result(seconds)

        self.subscribe("CASIO_TIMER", get_timer)
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
