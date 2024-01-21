import asyncio
from enum import IntEnum
from typing import Any

from utils import to_compact_string, to_hex_string
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class DtsState(IntEnum):
    ZERO = 0
    TWO = 2
    FOUR = 4


# class ReminderMasks:
#     YEARLY_MASK = 0b00001000
#     MONTHLY_MASK = 0b00010000
#     WEEKLY_MASK = 0b00000100

#     SUNDAY_MASK = 0b00000001
#     MONDAY_MASK = 0b00000010
#     TUESDAY_MASK = 0b00000100
#     WEDNESDAY_MASK = 0b00001000
#     THURSDAY_MASK = 0b00010000
#     FRIDAY_MASK = 0b00100000
#     SATURDAY_MASK = 0b01000000

#     ENABLED_MASK = 0b00000001


class DstWatchStateIO:
    result: asyncio.Future[Any] = None
    connection = None

    @staticmethod
    async def request(connection, state: DtsState):
        print(f"DstWatchStateIO request")
        DstWatchStateIO.connection = connection
        key = f"1d0{state.value}"
        await connection.request(key)

        loop = asyncio.get_running_loop()
        DstWatchStateIO.result = loop.create_future()
        return DstWatchStateIO.result

    @staticmethod
    async def send_to_watch(connection):
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_DST_WATCH_STATE"]]))

    @staticmethod
    def on_received(data):
        print(f"DstWatchStateIO onReceived")
        DstWatchStateIO.result.set_result(data)
