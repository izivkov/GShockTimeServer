import asyncio
import json
from typing import Any
from gshock_api.alarms import alarms_inst, alarm_decoder

from gshock_api.cancelable_result import CancelableResult
from gshock_api.utils import to_compact_string, to_hex_string
from gshock_api.casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS

class AlarmsIO:
    result: CancelableResult = None
    connection = None

    @staticmethod
    async def request(connection):
        AlarmsIO.connection = connection

        alarms_inst.clear()
        await AlarmsIO._get_alarms(connection)
        return AlarmsIO.result

    @staticmethod
    async def _get_alarms(connection):
        await connection.sendMessage("""{ "action": "GET_ALARMS"}""")

        AlarmsIO.result = CancelableResult()
        return await AlarmsIO.result.get_result()

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
        alarms_inst.add_alarms(decoded)

        if len(alarms_inst.alarms) == 5:
            AlarmsIO.result.set_result(alarms_inst.alarms)
