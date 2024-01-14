import asyncio
import json
from typing import Any

from utils import (
    clean_str,
    dec_to_hex,
    to_ascii_string,
    to_compact_string,
    to_hex_string,
    to_int_array,
)
from casio_constants import CasioConstants

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class ReminderMasks:
    YEARLY_MASK = 0b00001000
    MONTHLY_MASK = 0b00010000
    WEEKLY_MASK = 0b00000100

    SUNDAY_MASK = 0b00000001
    MONDAY_MASK = 0b00000010
    TUESDAY_MASK = 0b00000100
    WEDNESDAY_MASK = 0b00001000
    THURSDAY_MASK = 0b00010000
    FRIDAY_MASK = 0b00100000
    SATURDAY_MASK = 0b01000000

    ENABLED_MASK = 0b00000001


class EventsIO:
    result: asyncio.Future[Any] = None
    connection = None
    title = None

    @staticmethod
    async def request(connection, event_number):
        print(f"EventsIO request")
        EventsIO.connection = connection

        await connection.request("30{}".format(event_number))  # reminder title
        await connection.request("31{}".format(event_number))  # reminder time

        loop = asyncio.get_running_loop()
        EventsIO.result = loop.create_future()
        return EventsIO.result

    @staticmethod
    def send_to_watch_set(message):
        print(f"EventsIO sendToWatchSet: {message}")

    @staticmethod
    def on_received(message):
        print(f"EventsIO onReceived: {message}")

        def reminder_time_to_json(reminder_str):
            def convert_array_list_to_json_array(array_list):
                json_array = []
                for item in array_list:
                    json_array.append(item)

                return json_array

            def decode_time_period(time_period: int) -> tuple:
                enabled = False
                repeat_period = ""

                if (
                    time_period & ReminderMasks.ENABLED_MASK
                    == ReminderMasks.ENABLED_MASK
                ):
                    enabled = True

                if time_period & ReminderMasks.WEEKLY_MASK == ReminderMasks.WEEKLY_MASK:
                    repeat_period = "WEEKLY"
                elif (
                    time_period & ReminderMasks.MONTHLY_MASK
                    == ReminderMasks.MONTHLY_MASK
                ):
                    repeat_period = "MONTHLY"
                elif (
                    time_period & ReminderMasks.YEARLY_MASK == ReminderMasks.YEARLY_MASK
                ):
                    repeat_period = "YEARLY"
                else:
                    repeat_period = "NEVER"

                return (enabled, repeat_period)

            def decode_time_detail(time_detail):
                def decode_date(time_detail):
                    def int_to_month_str(month_int):
                        months = [
                            "JANUARY",
                            "FEBRUARY",
                            "MARCH",
                            "APRIL",
                            "MAY",
                            "JUNE",
                            "JULY",
                            "AUGUST",
                            "SEPTEMBER",
                            "OCTOBER",
                            "NOVEMBER",
                            "DECEMBER",
                        ]
                        if month_int < 1 or month_int > 12:
                            return ""
                        else:
                            return months[month_int - 1]

                    date = json.loads("{}")

                    date["year"] = dec_to_hex(time_detail[0]) + 2000
                    date["month"] = int_to_month_str(dec_to_hex(time_detail[1]))
                    date["day"] = dec_to_hex(time_detail[2])

                    return date

                result = {}

                #                  00 23 02 21 23 02 21 00 00
                # start from here:    ^
                # so, skip 1
                start_date = decode_date(time_detail[1:])

                result["start_date"] = start_date

                #                  00 23 02 21 23 02 21 00 00
                # start from here:             ^
                # so, skip 4
                end_date = decode_date(time_detail[4:])

                result["end_date"] = end_date

                day_of_week = time_detail[7]
                days_of_week = []
                if day_of_week & ReminderMasks.SUNDAY_MASK == ReminderMasks.SUNDAY_MASK:
                    days_of_week.append("SUNDAY")
                if day_of_week & ReminderMasks.MONDAY_MASK == ReminderMasks.MONDAY_MASK:
                    days_of_week.append("MONDAY")
                if (
                    day_of_week & ReminderMasks.TUESDAY_MASK
                    == ReminderMasks.TUESDAY_MASK
                ):
                    days_of_week.append("TUESDAY")
                if (
                    day_of_week & ReminderMasks.WEDNESDAY_MASK
                    == ReminderMasks.WEDNESDAY_MASK
                ):
                    days_of_week.append("WEDNESDAY")
                if (
                    day_of_week & ReminderMasks.THURSDAY_MASK
                    == ReminderMasks.THURSDAY_MASK
                ):
                    days_of_week.append("THURSDAY")
                if day_of_week & ReminderMasks.FRIDAY_MASK == ReminderMasks.FRIDAY_MASK:
                    days_of_week.append("FRIDAY")
                if (
                    day_of_week & ReminderMasks.SATURDAY_MASK
                    == ReminderMasks.SATURDAY_MASK
                ):
                    days_of_week.append("SATURDAY")
                result["days_of_week"] = days_of_week
                return result

            reminder_str_hex = to_hex_string(reminder_str)
            int_arr = to_int_array(reminder_str_hex)
            if int_arr[3] == 0xFF:
                # 0XFF indicates end of reminders
                return json.dumps({"end": ""})

            reminder_all = to_int_array(reminder_str_hex)
            # Remove the first 2 chars:
            # 0x31 05 <--- 00 23 02 21 23 02 21 00 00
            reminder = reminder_all[2:]
            reminder_json = {}
            time_period = decode_time_period(reminder[0])
            reminder_json["enabled"] = time_period[0]
            reminder_json["repeat_period"] = time_period[1]

            time_detail_map = decode_time_detail(reminder)

            reminder_json["start_date"] = time_detail_map["start_date"]
            reminder_json["end_date"] = time_detail_map["end_date"]
            reminder_json["days_of_week"] = convert_array_list_to_json_array(
                time_detail_map["days_of_week"]
            )

            return json.dumps({"time": reminder_json})

        reminder_json = {}
        value = reminder_time_to_json(message[2:])
        return reminder_json

    @staticmethod
    def on_received_title(message):
        print(f"EventsIO onReceivedTitle: {message}")
        EventsIO.title = ReminderDecoder.reminder_title_to_json(message)
        print(f"EventsIO title: {EventsIO.title}")


class ReminderDecoder:
    def reminder_title_to_json(title_byte: str) -> dict:
        hex_str = to_hex_string(title_byte)
        # ascii_str = to_ascii_string(hex_str, 2)

        int_arr = to_int_array(hex_str)
        if int_arr[2] == 0xFF:
            # 0XFF indicates end of reminders
            return {"end": ""}
        reminder_json = {}

        reminder_json["title"] = clean_str(to_ascii_string(hex_str, 2))
        return reminder_json
