import asyncio
import json
from typing import Any
from settings import settings
from utils import to_compact_string, to_hex_string, to_int_array
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class TimeAdjustmentIO:
    result: asyncio.Future[Any] = None
    connection = None

    @staticmethod
    async def request(connection):
        print(f"TimerIO request")
        TimeAdjustmentIO.connection = connection
        await connection.request("11")

        loop = asyncio.get_running_loop()
        TimeAdjustmentIO.result = loop.create_future()
        return TimeAdjustmentIO.result

    @staticmethod
    def send_to_watch(message):
        print(f"TimeAdjustmentIO sendToWatch: {message}")
        TimeAdjustmentIO.connection.write(
            0x000C, bytearray([CHARACTERISTICS["TIME_ADJUSTMENT"]])
        )

    @staticmethod
    def send_to_watch_set(message):
        print(f"TimeAdjustmentIO sendToWatchSet: {message}")

    @staticmethod
    def on_received(message):
        print(f"TimeAdjustmentIO onReceived: {message}")

        data = to_hex_string(message)
        json_data = json.loads(data).get("timeAdjustment")

        TimeAdjustmentIO.result.set_result(message)
