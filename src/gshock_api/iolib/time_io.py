import asyncio
import datetime
import json
import time
from typing import Any
from logger import logger

from utils import to_compact_string, to_hex_string
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class TimeIO:
    result: asyncio.Future[Any] = None
    connection = None

    @staticmethod
    async def request(connection, current_time):
        TimeIO.connection = connection

        if current_time is None:
            current_time = time.time()

        message = {
            "action": "SET_TIME",
            "value": "{}".format(round(current_time * 1000)),
        }
        await connection.sendMessage(json.dumps(message))

    @staticmethod
    async def send_to_watch_set(message):
        date_time_ms = int(json.loads(message).get("value"))
        logger.info("date_time_ms: {}".format(date_time_ms))
        date_time = datetime.datetime.fromtimestamp(date_time_ms / 1000.0)
        time_data = TimeEncoder.prepare_current_time(date_time)
        time_command = to_hex_string(
            bytearray([CHARACTERISTICS["CASIO_CURRENT_TIME"]]) + time_data
        )
        await TimeIO.connection.write(0xE, to_compact_string(time_command))


class TimeEncoder:
    def prepare_current_time(date: datetime.datetime):
        arr = bytearray(10)
        year = date.year
        arr[0] = year >> 0 & 0xFF
        arr[1] = year >> 8 & 0xFF
        arr[2] = date.month
        arr[3] = date.day
        arr[4] = date.hour
        arr[5] = date.minute
        arr[6] = date.second
        arr[7] = date.weekday()
        arr[8] = 0
        arr[9] = 1
        return arr
