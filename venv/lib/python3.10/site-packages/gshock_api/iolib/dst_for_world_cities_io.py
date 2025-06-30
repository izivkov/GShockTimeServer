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
        DstForWorldCitiesIO.connection = connection
        key = "1e0{}".format(city_number)
        await connection.request(key)

        DstForWorldCitiesIO.result = CancelableResult()
        return DstForWorldCitiesIO.result.get_result()

    @staticmethod
    async def send_to_watch(connection):
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_DST_SETTING"]]))

    @staticmethod
    def on_received(data):
        DstForWorldCitiesIO.result.set_result(data)
