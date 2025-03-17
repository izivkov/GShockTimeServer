import asyncio
from typing import Any
from gshock_api.cancelable_result import CancelableResult
from gshock_api.logger import logger

from gshock_api.utils import to_compact_string, to_hex_string
from gshock_api.casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS

class DstForWorldCitiesIO:
    result: CancelableResult = None
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
