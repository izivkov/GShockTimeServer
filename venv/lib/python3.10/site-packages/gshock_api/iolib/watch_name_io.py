import asyncio
from typing import Any

from gshock_api.casio_constants import CasioConstants
from gshock_api.utils import clean_str, to_ascii_string, to_hex_string
from gshock_api.cancelable_result import CancelableResult


class WatchNameIO:
    result: CancelableResult = None
    connection = None

    @staticmethod
    async def request(connection):
        WatchNameIO.connection = connection
        await connection.request("23")

        WatchNameIO.result = CancelableResult()
        return WatchNameIO.result.get_result()

    @staticmethod
    def on_received(data):
        hex_str = to_hex_string(data)
        ascii_str = to_ascii_string(hex_str, 1)
        clean_data = clean_str(ascii_str)
        WatchNameIO.result.set_result(clean_data)

    @staticmethod
    async def send_to_watch():
        pass
