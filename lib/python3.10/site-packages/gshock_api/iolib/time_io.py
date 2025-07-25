import time
import datetime
import json
import time
from typing import Any
from gshock_api.logger import logger

from gshock_api.utils import to_compact_string, to_hex_string
from gshock_api.casio_constants import CasioConstants
from gshock_api.exceptions import GShockIgnorableException

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class TimeIO:
    connection = None

    @staticmethod
    async def request(connection, current_time, offset):
        TimeIO.connection = connection

        message = {
            "action": "SET_TIME",
            "value": {
                "time": None if current_time is None else round(current_time),
                "offset": offset  # must always be an integer
            }
        }
        await connection.sendMessage(json.dumps(message))

    @staticmethod
    async def send_to_watch_set(message):
        data = json.loads(message)
        value = data.get("value", {})

        # Extract time (or use current time), and apply offset (or default to 0)
        timestamp = value.get("time")
        offset = value.get("offset", 0)

        # Fall back to current time if timestamp is None
        if timestamp is None:
            timestamp = time.time()

        date_time_ms = int(timestamp + offset)

        date_time = datetime.datetime.fromtimestamp(date_time_ms)
        time_data = TimeEncoder.prepare_current_time(date_time)
        time_command = to_hex_string(
            bytearray([CHARACTERISTICS["CASIO_CURRENT_TIME"]]) + time_data
        )
        try:
            await TimeIO.connection.write(0xE, to_compact_string(time_command))
        except (GShockIgnorableException) as e:
            # Ignore this exception if the LOWER-RIGHT button is pressed.
            # In this case, the connection will be closed before the call completes with a response, and we get an EOFError.
            # The call actually works, though.
            logger.info(f"Ignoring {e}")

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
