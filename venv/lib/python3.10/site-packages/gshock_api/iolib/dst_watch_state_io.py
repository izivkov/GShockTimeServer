import asyncio
from enum import IntEnum
from typing import Any
from gshock_api.cancelable_result import CancelableResult
from gshock_api.logger import logger
from gshock_api.utils import to_compact_string, to_hex_string
from gshock_api.casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class DtsState(IntEnum):
    ZERO = 0
    TWO = 2
    FOUR = 4

class DstWatchStateIO:
    result: CancelableResult = None
    connection = None

    @staticmethod
    async def request(connection, state: DtsState):
        DstWatchStateIO.connection = connection
        key = f"1d0{state.value}"
        await connection.request(key)

        DstWatchStateIO.result = CancelableResult()
        return DstWatchStateIO.result.get_result()


    @staticmethod
    async def send_to_watch(connection):
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_DST_WATCH_STATE"]]))

    @staticmethod
    def on_received(data):
        DstWatchStateIO.result.set_result(data)
