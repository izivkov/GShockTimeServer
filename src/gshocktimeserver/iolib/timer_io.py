import asyncio
from typing import Any

import connection
from utils import to_compact_string, to_hex_string
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class TimerIO:
    result: asyncio.Future[Any] = None

    @staticmethod
    async def request(connection):
        print(f"TimerIO request")
        await connection.request("18")

        loop = asyncio.get_running_loop()
        TimerIO.result = loop.create_future()
        return TimerIO.result

    @staticmethod
    async def send_to_watch(message):
        print(f"TimerIO sendToWatch: {message}")
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_TIMER"]]))

    @staticmethod
    async def send_to_watch_set(data):
        print(f"TimerIO sendToWatchSet: {data}")

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

        seconds_as_byte_arr = encode(data)
        seconds_as_compact_str = to_compact_string(to_hex_string(seconds_as_byte_arr))
        await connection.write(0x000E, seconds_as_compact_str)

    @staticmethod
    def on_received(data):
        print(f"TimerIO onReceived")

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
