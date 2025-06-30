import asyncio
import json
import logging
from typing import Any
from gshock_api.cancelable_result import CancelableResult
from gshock_api.settings import settings
from gshock_api.utils import to_compact_string, to_hex_string, to_int_array
from gshock_api.casio_constants import CasioConstants
from gshock_api.iolib.error_io import ErrorIO
from gshock_api.logger import logger


CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class TimeAdjustmentIO:
    result: CancelableResult = None
    connection = None
    original_value = None

    @staticmethod
    async def request(connection):
        TimeAdjustmentIO.connection = connection
        await connection.request("11")

        TimeAdjustmentIO.result = CancelableResult()
        return TimeAdjustmentIO.result.get_result()


    @staticmethod
    def send_to_watch(message):
        TimeAdjustmentIO.connection.write(
            0x000C, bytearray([CHARACTERISTICS["TIME_ADJUSTMENT"]])
        )

    @staticmethod
    async def send_to_watch_set(message):

        if TimeAdjustmentIO.original_value == None:
            return ErrorIO.request("Error: Must call get before set")

        time_adjustment = json.loads(message).get("timeAdjustment") == "True"
        minutes_after_hour = int(json.loads(message).get("minutesAfterHour"))

        def encode_time_adjustment(time_adjustment, minutes_after_hour):
            raw_string = TimeAdjustmentIO.original_value
            "0x11 0F 0F 0F 06 00 00 00 00 00 01 00 80 30 30"
            int_array = to_int_array(raw_string)
            int_array[12] = 0x80 if time_adjustment == False else 0x00
            int_array[13] = int(minutes_after_hour)
            return bytes(int_array)

        encoded_time_adj = encode_time_adjustment(time_adjustment, minutes_after_hour)

        write_cmd = to_compact_string(to_hex_string(encoded_time_adj))
        await TimeAdjustmentIO.connection.write(0x000E, write_cmd)

    @staticmethod
    def on_received(message):
        TimeAdjustmentIO.original_value = to_hex_string(
            message
        )  # save original message

        def is_time_adjustment_set(data) -> bool:
            # syncing off: 110f0f0f0600500004000100->80<-10d2
            # syncing on:  110f0f0f0600500004000100->00<-10d2

            # CasioIsAutoTimeOriginalValue.value = data  # save original data for future use
            return int(data[12]) == 0x00

        def get_minutes_after_hour(data) -> int:
            # syncing off: 110f0f0f060050000400010080->10<-d2

            # CasioIsAutoTimeOriginalValue.value = data  # save original data for future use
            return int(data[13])

        timeAdjusted = is_time_adjustment_set(message)
        munutesAfterHour = get_minutes_after_hour(message)
        valueToSetStr = f"""{{"timeAdjusment": "{timeAdjusted}",
            "minutesAfterHour": "{munutesAfterHour}" }}"""

        value = json.loads(valueToSetStr)
        TimeAdjustmentIO.result.set_result(value)

    @staticmethod
    async def on_received_set(message):
        logger.info(f"TimeAdjustmentIO onReceivedSet: {message}")
