import asyncio
import logging
import json
import time

from connection import Connection
from data_watcher import dataWatcher
from utils import to_ascii_string, trimNonAsciiCharacters, to_int_array, to_compact_string, current_milli_time
from result_queue import result_queue, KeyedResult
from casio_watch import WATCH_BUTTON, DTS_STATE
from alarms import alarmsInst
from event import Event

class GshockAPI:
    logger = logging.getLogger("GshockAPI")

    def __init__(self, connection):
        self.connection = connection

    async def getWatchName(self):
        return await self._getWatchName("23")
    
    async def _getWatchName(self, key):
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def onDataReceived (keyedData):
            _key = "23"
            
            resultValue = keyedData["value"]
            resultKey = keyedData["key"]
            
            if (resultKey == _key):
                resultStr = trimNonAsciiCharacters(toAsciiString(resultValue, 1))
                res = result_queue.dequeue(_key)
                res.set_result(resultStr)

        self.subscribe("CASIO_WATCH_NAME", lambda data: onDataReceived(data))
        return await result

    ######################
    async def getPressedButton(self) -> WATCH_BUTTON:
        return await self._getPressedButton("10")    

    async def _getPressedButton(self, key: str) -> WATCH_BUTTON:
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def button_pressed_callback(keyedData):
            """
            RIGHT BUTTON: 0x10 17 62 07 38 85 CD 7F ->04<- 03 0F FF FF FF FF 24 00 00 00
            LEFT BUTTON:  0x10 17 62 07 38 85 CD 7F ->01<- 03 0F FF FF FF FF 24 00 00 00
            RESET:        0x10 17 62 16 05 85 dd 7f ->00<- 03 0f ff ff ff ff 24 00 00 00 // after watch reset
            AUTO-TIME:    0x10 17 62 16 05 85 dd 7f ->03<- 03 0f ff ff ff ff 24 00 00 00 // no button pressed
            """
            
            resultValue = keyedData["value"]
            resultKey = keyedData["key"]

            ret = WATCH_BUTTON.INVALID

            if resultKey == "10" and resultValue != "" and len(to_int_array(resultValue)) >= 19:
                bleIntArr = to_int_array(resultValue)
                button_indicator = bleIntArr[8]
                ret = WATCH_BUTTON.LOWER_LEFT if (button_indicator == 0 or button_indicator == 1) else \
                    WATCH_BUTTON.LOWER_RIGHT if button_indicator == 4 else \
                    WATCH_BUTTON.NO_BUTTON if button_indicator == 3 else \
                    WATCH_BUTTON.INVALID
            
                res = result_queue.dequeue("10")
                res.set_result(ret)

        self.subscribe("BUTTON_PRESSED", button_pressed_callback)
        
        return await result

    ###################

    async def getWorldCities(self, cityNumber: int):
        key = "1f0{}".format(cityNumber)
        return await self._getWorldCities(key)

    async def _getWorldCities(self, key: str):
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def casio_world_cities_callback (keyedData):
            value = keyedData["value"]
            key = keyedData["key"]

            res = result_queue.dequeue(key)
            res.set_result(value)

        def process_home_time(keyedData):
            value = keyedData["value"]
            key = keyedData["key"]
            self.logger.info("Got HOME_TIME: {}".format(toAsciiString(value, 1)))

        self.subscribe("CASIO_WORLD_CITIES", casio_world_cities_callback)
        # self.subscribe("HOME_TIME", process_home_time)
        return await result

    async def getDSTForWorldCities(self, cityNumber: int) -> str:
        key = "1e0{}".format(cityNumber)
        return await self._getDSTForWorldCities(key)

    async def _getDSTForWorldCities(self, key: str) -> str:
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def casio_dts_world_cities_callback (keyedData):
            value = keyedData["value"]
            key = keyedData["key"]

            res = result_queue.dequeue(key)
            res.set_result(value)

        self.subscribe("CASIO_DST_SETTING", casio_dts_world_cities_callback)

        return await result

    async def getDSTWatchState(self, state: DTS_STATE) -> str:
        key = f"1d0{state.value}"
        return await self._getDSTWatchState(key)

    async def _getDSTWatchState(self, key: str) -> str:
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def handleMessage(keyedData):
            value = keyedData["value"]
            key = keyedData["key"]

            res = result_queue.dequeue(key)
            res.set_result(value)
        
        self.subscribe("CASIO_DST_WATCH_STATE", handleMessage)

        return await result

    async def initializeForSettingTime(self):
        # Before we can set time, we must read and write back these values.
        # Why? Not sure, ask Casio

        async def readAndWrite(function, param):
            ret = await function(param)
            shortStr = to_compact_string(ret)
            await self.connection.write(0xE, shortStr)

        await readAndWrite(self.getDSTWatchState, DTS_STATE.ZERO)
        await readAndWrite(self.getDSTWatchState, DTS_STATE.TWO)
        await readAndWrite(self.getDSTWatchState, DTS_STATE.FOUR)

        await readAndWrite(self.getDSTForWorldCities, 0)
        await readAndWrite(self.getDSTForWorldCities, 1)
        await readAndWrite(self.getDSTForWorldCities, 2)
        await readAndWrite(self.getDSTForWorldCities, 3)
        await readAndWrite(self.getDSTForWorldCities, 4)
        await readAndWrite(self.getDSTForWorldCities, 5)

        await readAndWrite(self.getWorldCities, 0)
        await readAndWrite(self.getWorldCities, 1)
        await readAndWrite(self.getWorldCities, 2)
        await readAndWrite(self.getWorldCities, 3)
        await readAndWrite(self.getWorldCities, 4)
        await readAndWrite(self.getWorldCities, 5)
        
    async def setTime(self, changeHomeTime=True):
        await self.initializeForSettingTime()

        message = {"action": "SET_TIME", "value": "{}".format(round(time.time() * 1000)) }
        await self.connection.sendMessage(json.dumps(message))

    async def getAlarms(self):
        alarmsInst.clear()
        await self._getAlarms()
        await self._getAlarms2()
        return alarmsInst.alarms
    
    async def _getAlarms(self):
        await self.connection.sendMessage("""{ "action": "GET_ALARMS"}""")
        key = "GET_ALARMS"

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def alarms_received(keyedData):
            data = keyedData["value"]
            key = "GET_ALARMS"

            alarmsInst.addAlarms(data)
            
            res = result_queue.dequeue(key)
            res.set_result(data)

        self.subscribe("ALARMS", alarms_received)
        return await result

    async def _getAlarms2(self):
        await self.connection.sendMessage("""{ "action": "GET_ALARMS2"}""")
        key = "GET_ALARMS2"

        # Alarm.alarms.clear()

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def alarms_received2(keyedData):
            data = keyedData["value"]
            key = "GET_ALARMS2"

            alarmsInst.addAlarms(data)
            
            res = result_queue.dequeue(key)
            res.set_result(data)

        self.subscribe("ALARMS2", alarms_received2)
        return await result
    

    async def setAlarms(self, alarms):
        if not alarms:
            self.logger.info("Alarm model not initialised! Cannot set alarm")
            return

        alarmsStr = json.dumps(alarms)
        setActionCmd = '{{"action":"SET_ALARMS", "value":{} }}'.format(alarmsStr)
        await self.connection.sendMessage(setActionCmd)
        self.logger.info("Returning from setAlarms")

    ############################
    async def getTimer(self):
        return await self._getTimer("18")

    async def _getTimer(self, key):
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def decodeValue(data: str) -> str:
            timerIntArray = to_int_array(data)

            hours = timerIntArray[1]
            minutes = timerIntArray[2]
            seconds = timerIntArray[3]

            inSeconds = hours * 3600 + minutes * 60 + seconds
            return inSeconds

        def getTimer(keyedData):
            value = keyedData["value"]
            key = keyedData["key"]

            seconds = decodeValue(value)
            res = result_queue.dequeue(key)
            res.set_result(seconds)

        self.subscribe("CASIO_TIMER", getTimer)
        return await result

    async def setTimer(self, timerValue):
        # cache.remove("18")
        await self.connection.sendMessage("""{"action": "SET_TIMER", "value": """+str(timerValue)+""" }""")

    async def get_time_adjustment(self):
        # await self.connection.sendMessage("""{ "action": "GET_TIME_ADJUSTMENT"}""")

        key = "11"
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def get_time_adjustment(keyed_data):
            value = keyed_data["value"]
            key = keyed_data["key"]
            if (key != "11"):
                return

            res = result_queue.dequeue(key)
            time_adjustment = value.get("timeAdjustment", False) == True
            res.set_result(time_adjustment)

        self.subscribe("TIME_ADJUSTMENT", get_time_adjustment)
        return await result
    
    async def set_time_adjustment(self, settings):
        await self.connection.sendMessage("""{"action": "SET_TIME_ADJUSTMENT", "value": \""""+str(settings.timeAdjustment)+"""\" }""")

    async def get_basic_settings(self):
        key = "13"
        await self.connection.request(key)

        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def _get_settings(keyed_data):
            value = keyed_data["value"]
            key = keyed_data["key"]

            settings = json.loads (value)
            res = result_queue.dequeue(key)
            res.set_result(settings)

        self.subscribe("SETTINGS", _get_settings)
        return await result
    
    async def set_settings(self, settings):
        setting_json = json.dumps(settings)
        await self.connection.sendMessage("""{"action": "SET_SETTINGS", "value": """+setting_json+""" }""")

    async def get_reminders (self):
        reminders = []

        reminders.append(await self.getEventFromWatch(1))
        reminders.append(await self.getEventFromWatch(2))
        reminders.append(await self.getEventFromWatch(3))
        reminders.append(await self.getEventFromWatch(4))
        reminders.append(await self.getEventFromWatch(5))

        return reminders

    async def getEventFromWatch(self, eventNumber: int): 
        await self.connection.request("30{}".format(eventNumber))  # reminder title
        await self.connection.request("31{}".format(eventNumber))  # reminder time
    
        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult("310{}".format(eventNumber), result))
    
        def get_reminders(keyed_data):
            value = keyed_data["value"]
            key = keyed_data["key"]

            for obj_key in value:
                if obj_key == "title":
                    self.title = value[obj_key]

                elif obj_key == "time":
                    json_obj = json.loads("{}")
                    json_obj["title"] = self.title
                    json_obj["time"] = value["time"]
                    event_obj = Event()
                    event = event_obj.createEvent(json_obj)

                    res = result_queue.dequeue(key)
                    res.set_result(event)

        self.subscribe("REMINDERS", get_reminders)
        return await result

    async def set_remonders(self, events: list):
        if not events:
            return
        
        def to_json(events: list):
            events_json = json.loads("[]")
            for event in events:
                event_json = json.loads(json.dumps(event.__dict__))
                events_json.append(event_json)

            return events_json

        def getSelectedEvents(events: list):
            selectedEvents = [event for event in events if event.selected]
            return to_json(selectedEvents)
        
        selected = getSelectedEvents(events)

        await self.connection.sendMessage("""{{\"action\": \"SET_REMINDERS\", \"value\": {}}}""".format(json.dumps(selected)))


    #####################
    async def get_app_info(self):
        key = "22"
        await self.connection.request(key)
    
        def set_app_info(data: str):
            # App info:
            # This is needed to re-enable button D (Lower-right) after the watch has been reset or BLE has been cleared.
            # It is a hard-coded value, which is what the official app does as well.

            # If watch was reset, the app info will come as:
            # 0x22 FF FF FF FF FF FF FF FF FF FF 00
            # In this case, set it to the hardcoded value bellow, so 'D' button will work again.
            app_info_compact_str = to_compact_string(data)
            if app_info_compact_str == "22FFFFFFFFFFFFFFFFFFFF00":
                self.connection.write(0xE, "223488F4E5D5AFC829E06D02")
        
        loop = asyncio.get_running_loop()
        result = loop.create_future()
        result_queue.enqueue(KeyedResult(key, result))

        def subscribe_casio_app_information(keyed_data):
            data = keyed_data["value"]
            key = keyed_data["key"]

            set_app_info(data)
            res = result_queue.dequeue(key)
            res.set_result("")
            
        self.subscribe("CASIO_APP_INFORMATION", subscribe_casio_app_information)
        return await result

    ############################
    def subscribe(self, subjectName, on_next) -> None:
        dataWatcher.add_subject(subjectName)    
        dataWatcher.subscribe("GshockAPI", subjectName, on_next)