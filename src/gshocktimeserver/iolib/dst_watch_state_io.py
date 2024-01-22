import asyncio
from enum import IntEnum
from typing import Any
from logger import logger
from utils import to_compact_string, to_hex_string
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class DtsState(IntEnum):
    ZERO = 0
    TWO = 2
    FOUR = 4


class DstWatchStateIO:
    result: asyncio.Future[Any] = None
    connection = None

    @staticmethod
    async def request(connection, state: DtsState):
        logger.info(f"DstWatchStateIO request")
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
        logger.info(f"DstWatchStateIO onReceived")
        DstWatchStateIO.result.set_result(data)
