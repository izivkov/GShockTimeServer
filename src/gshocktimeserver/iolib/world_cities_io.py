import asyncio
from typing import Any
from casio_watch import DtsState

from utils import to_compact_string, to_hex_string
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class WorldCitiesIO:
    result: asyncio.Future[Any] = None
    connection = None

    @staticmethod
    async def request(connection, cityNumber: int):
        print(f"DstWatchStateIO request")
        WorldCitiesIO.connection = connection
        key = "1f0{}".format(cityNumber)

        await connection.request(key)

        loop = asyncio.get_running_loop()
        WorldCitiesIO.result = loop.create_future()
        return WorldCitiesIO.result

    @staticmethod
    async def send_to_watch(connection):
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_WORLD_CITIES"]]))

    @staticmethod
    def on_received(data):
        print(f"WorldCitiesIO onReceived")
        WorldCitiesIO.result.set_result(data)
