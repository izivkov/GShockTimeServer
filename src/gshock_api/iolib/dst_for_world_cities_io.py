import asyncio
from typing import Any
from logger import logger

from utils import to_compact_string, to_hex_string
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class DstForWorldCitiesIO:
    result: asyncio.Future[Any] = None
    connection = None

    @staticmethod
    async def request(connection, city_number: int):
        logger.info(f"DstForWorldCitiesIO request")
        DstForWorldCitiesIO.connection = connection
        key = "1e0{}".format(city_number)
        await connection.request(key)

        loop = asyncio.get_running_loop()
        DstForWorldCitiesIO.result = loop.create_future()
        return DstForWorldCitiesIO.result

    @staticmethod
    async def send_to_watch(connection):
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_DST_SETTING"]]))

    @staticmethod
    def on_received(data):
        logger.info(f"DstForWorldCitiesIO onReceived")
        DstForWorldCitiesIO.result.set_result(data)
