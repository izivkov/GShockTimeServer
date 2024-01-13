import asyncio
from typing import Any
from casio_watch import DtsState

from utils import to_compact_string, to_hex_string
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


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
