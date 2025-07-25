import asyncio
import json
from typing import Any
from gshock_api.cancelable_result import CancelableResult
from gshock_api.logger import logger

from gshock_api.utils import to_compact_string, to_hex_string
from gshock_api.casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class TimerIO:
    result: CancelableResult = None
    connection = None

    @staticmethod
    async def request(connection):
        TimerIO.connection = connection
        await connection.request("18")

        TimerIO.result = CancelableResult()
        return TimerIO.result.get_result()


    @staticmethod
    async def send_to_watch(connection):
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_TIMER"]]))

    @staticmethod
    async def send_to_watch_set(data):
        def encode(seconds_str):
            in_seconds = int(seconds_str)
            hours = in_seconds // 3600
            minutes_and_seconds = in_seconds % 3600
            minutes = minutes_and_seconds // 60
            seconds = minutes_and_seconds % 60

            arr = bytearray(7)
            arr[0] = 0x18
            arr[1] = hours
            arr[2] = minutes
            arr[3] = seconds
            return arr

        data_obj = json.loads(data)
        seconds_as_byte_arr = encode(data_obj.get("value"))
        seconds_as_compact_str = to_compact_string(to_hex_string(seconds_as_byte_arr))
        await TimerIO.connection.write(0x000E, seconds_as_compact_str)

    @staticmethod
    def on_received(data):
        def decode_value(data: str) -> str:
            timer_int_array = data

            hours = timer_int_array[1]
            minutes = timer_int_array[2]
            seconds = timer_int_array[3]

            in_seconds = hours * 3600 + minutes * 60 + seconds
            return in_seconds

        decoded = decode_value(data)
        seconds = int(decoded)
        TimerIO.result.set_result(seconds)
