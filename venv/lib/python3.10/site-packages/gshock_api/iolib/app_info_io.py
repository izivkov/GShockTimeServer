import asyncio
from typing import Any
from gshock_api.cancelable_result import CancelableResult
from gshock_api.logger import logger

from gshock_api.utils import to_compact_string, to_hex_string
from gshock_api.casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class AppInfoIO:
    result: CancelableResult = None
    connection = None

    @staticmethod
    async def request(connection):
        AppInfoIO.connection = connection
        await connection.request("22")

        AppInfoIO.result = CancelableResult()
        return AppInfoIO.result.get_result()

    @staticmethod
    async def send_to_watch(connection):
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_APP_INFORMATION"]]))

    @staticmethod
    def on_received(data):
        def set_app_info(data: str):
            # App info:
            # This is needed to re-enable button D (Lower-right) after the watch has been reset or BLE has been cleared.
            # It is a hard-coded value, which is what the official app does as well.

            # If watch was reset, the app info will come as:
            # 0x22 FF FF FF FF FF FF FF FF FF FF 00
            # In this case, set it to the hardcoded value bellow, so 'D' button will
            # work again.
            app_info_compact_str = to_compact_string(data)
            if app_info_compact_str == "22FFFFFFFFFFFFFFFFFFFF00":
                AppInfoIO.connection.write(0xE, "223488F4E5D5AFC829E06D02")

        set_app_info(to_hex_string(data))
        AppInfoIO.result.set_result("OK")
