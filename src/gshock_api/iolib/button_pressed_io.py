import asyncio
from enum import IntEnum
from typing import Any
from logger import logger
from utils import to_compact_string, to_hex_string, to_int_array
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class WatchButton(IntEnum):
    UPPER_LEFT = 1
    LOWER_LEFT = 2
    UPPER_RIGHT = 3
    LOWER_RIGHT = 4
    NO_BUTTON = 5
    INVALID = 6

class ButtonPressedIO:
    result: asyncio.Future[Any] = None
    connection = None

    @staticmethod
    async def request(connection):
        logger.info(f"ButtonPressedIO request")
        ButtonPressedIO.connection = connection
        await connection.request("10")

        loop = asyncio.get_running_loop()
        ButtonPressedIO.result = loop.create_future()
        return ButtonPressedIO.result

    @staticmethod
    async def send_to_watch(connection):
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_BLE_FEATURES"]]))

    @staticmethod
    async def send_to_watch_set(data):
        logger.info(f"TimerIO sendToWatchSet: {data}")

        await ButtonPressedIO.connection.write(0x000E, data)

    @staticmethod
    def on_received(data):
        logger.info(f"ButtonPressedIO onReceived")

        def button_pressed_callback(data):
            """
            RIGHT BUTTON: 0x10 17 62 07 38 85 CD 7F ->04<- 03 0F FF FF FF FF 24 00 00 00
            LEFT BUTTON:  0x10 17 62 07 38 85 CD 7F ->01<- 03 0F FF FF FF FF 24 00 00 00
            RESET:        0x10 17 62 16 05 85 dd 7f ->00<- 03 0f ff ff ff ff 24 00 00 00 // after watch reset
            AUTO-TIME:    0x10 17 62 16 05 85 dd 7f ->03<- 03 0f ff ff ff ff 24 00 00 00 // no button pressed
            """

            ret = WatchButton.INVALID

            if len(data) >= 19:
                ble_int_arr = to_int_array(to_hex_string(data))
                button_indicator = ble_int_arr[8]
                ret = (
                    WatchButton.LOWER_LEFT
                    if (button_indicator == 0 or button_indicator == 1)
                    else WatchButton.LOWER_RIGHT
                    if button_indicator == 4
                    else WatchButton.NO_BUTTON
                    if button_indicator == 3
                    else WatchButton.INVALID
                )

            return ret

        button = button_pressed_callback(data)
        ButtonPressedIO.result.set_result(button)
