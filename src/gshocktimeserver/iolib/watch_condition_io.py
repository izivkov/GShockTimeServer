import asyncio
from typing import Any
from watch_info import WatchInfo
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class WatchConditionIO:
    result: asyncio.Future[Any] = None
    connection = None

    class WatchConditionValue:
        def __init__(self, battery_level_percent: int, temperature: int):
            self.battery_level_percent = battery_level_percent
            self.temperature = temperature

    @staticmethod
    async def request(connection):
        print(f"WatchConditionIO request")
        WatchConditionIO.connection = connection
        await connection.request("28")

        loop = asyncio.get_running_loop()
        WatchConditionIO.result = loop.create_future()
        return WatchConditionIO.result

    @staticmethod
    async def send_to_watch(connection):
        connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_WATCH_CONDITION"]]))

    @staticmethod
    def on_received(data):
        print(f"WatchConditionIO onReceived")

        def decode_value(data: str) -> WatchConditionIO.WatchConditionValue:
            int_arr = list(map(int, data))
            bytes_data = bytes(int_arr[1:])

            if len(bytes_data) >= 2:
                # Battery level between 15 and 20 for B2100 and between 12 and 19 for B5600. Scale accordingly to %
                print(f"battery level row value: {int(bytes_data[0])}")

                battery_level_lower_limit = (15 + 9) / 2
                battery_level_upper_limit = 19.5

                multiplier = round(
                    100.0 / (battery_level_upper_limit - battery_level_lower_limit)
                )
                battery_level = int(bytes_data[0]) - battery_level_lower_limit
                battery_level_percent = min(max(battery_level * multiplier, 0), 100)
                temperature = int(bytes_data[1])

                return WatchConditionIO.WatchConditionValue(
                    battery_level_percent, temperature
                )

            return WatchConditionIO.WatchConditionValue(0, 0)

        WatchConditionIO.result.set_result(decode_value(data))
