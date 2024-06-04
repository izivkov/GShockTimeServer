import asyncio
from typing import Any

from casio_constants import CasioConstants
from utils import clean_str, to_ascii_string, to_hex_string


class WatchNameIO:
    result: asyncio.Future[Any] = None
    connection = None

    @staticmethod
    async def request(connection):
        WatchNameIO.connection = connection
        await connection.request("23")

        loop = asyncio.get_running_loop()
        WatchNameIO.result = loop.create_future()
        return WatchNameIO.result

    @staticmethod
    def on_received(data):
        hex_str = to_hex_string(data)
        ascii_str = to_ascii_string(hex_str, 1)
        clean_data = clean_str(ascii_str)
        WatchNameIO.result.set_result(clean_data)

    @staticmethod
    async def send_to_watch():
        pass
