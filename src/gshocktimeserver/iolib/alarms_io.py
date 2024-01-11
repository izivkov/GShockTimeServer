import asyncio
import json
from typing import Any
from alarms import alarms_inst, alarm_decoder

from utils import to_compact_string, to_hex_string
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class AlarmsIO:
    result: asyncio.Future[Any] = None
    # result2: asyncio.Future[Any] = None
    connection = None

    @staticmethod
    async def request(connection):
        await connection.request("GET_ALARMS")
        AlarmsIO.connection = connection

        alarms_inst.clear()
        await AlarmsIO._get_alarms(connection)
        # await AlarmsIO._get_alarms2(connection)
        return AlarmsIO.result

    @staticmethod
    async def _get_alarms(connection):
        await connection.sendMessage("""{ "action": "GET_ALARMS"}""")
        # await connection.request("16")

        loop = asyncio.get_running_loop()
        AlarmsIO.result = loop.create_future()
        return AlarmsIO.result

    @staticmethod
    async def _get_alarms2(connection):
        await connection.sendMessage("""{ "action": "GET_ALARMS2"}""")
        # await connection.request("GET_ALARMS2")

        loop = asyncio.get_running_loop()
        AlarmsIO.result2 = loop.create_future()
        return AlarmsIO.result2

    @staticmethod
    async def send_to_watch(message=""):
        alarm_command = to_compact_string(
            to_hex_string(bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]]))
        )
        await AlarmsIO.connection.write(0x000C, alarm_command)

        alarm_command_2 = to_compact_string(
            to_hex_string(bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]]))
        )
        await AlarmsIO.connection.write(0x000C, alarm_command_2)

    @staticmethod
    async def send_to_watch_set(message):
        alarms_json_arr = json.loads(message).get("value")
        alarm_casio0 = to_compact_string(
            to_hex_string(alarms_inst.from_json_alarm_first_alarm(alarms_json_arr[0]))
        )
        await AlarmsIO.connection.write(0x000E, alarm_casio0)
        alarm_casio = to_compact_string(
            to_hex_string(alarms_inst.from_json_alarm_secondary_alarms(alarms_json_arr))
        )
        await AlarmsIO.connection.write(0x000E, alarm_casio)

    @staticmethod
    def on_received(data):
        decoded = alarm_decoder.to_json(to_hex_string(data))["ALARMS"]
        print(f"AlarmsIO onReceived: {decoded}")
        alarms_inst.add_alarms(decoded)
        print("len: len(alarms_inst.alarms): ", len(alarms_inst.alarms))

        if len(alarms_inst.alarms) == 5:
            AlarmsIO.result.set_result(alarms_inst.alarms)
