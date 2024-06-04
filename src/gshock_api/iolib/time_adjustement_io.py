import asyncio
import json
import logging
from typing import Any
from settings import settings
from utils import to_compact_string, to_hex_string, to_int_array
from casio_constants import CasioConstants
from iolib.error_io import ErrorIO
from logger import logger


CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class TimeAdjustmentIO:
    result: asyncio.Future[Any] = None
    connection = None
    original_value = None

    @staticmethod
    async def request(connection):
        logger.info(f"TimerIO request")
        TimeAdjustmentIO.connection = connection
        await connection.request("11")

        loop = asyncio.get_running_loop()
        TimeAdjustmentIO.result = loop.create_future()
        return TimeAdjustmentIO.result

    @staticmethod
    def send_to_watch(message):
        logger.info(f"TimeAdjustmentIO sendToWatch: {message}")
        TimeAdjustmentIO.connection.write(
            0x000C, bytearray([CHARACTERISTICS["TIME_ADJUSTMENT"]])
        )

    @staticmethod
    async def send_to_watch_set(message):
        logger.info(f"TimeAdjustmentIO sendToWatchSet: {message}")

        if TimeAdjustmentIO.original_value == None:
            logging.error("Error: Must call get before set")
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
        logger.info(f"TimeAdjustmentIO onReceived: {message}")
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
