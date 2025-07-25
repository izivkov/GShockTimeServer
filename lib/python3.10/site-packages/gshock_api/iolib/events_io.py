import asyncio
import json
from typing import Any
from gshock_api.cancelable_result import CancelableResult
from gshock_api.logger import logger
from gshock_api.casio_constants import CasioConstants

from gshock_api.utils import (
    clean_str,
    dec_to_hex,
    to_ascii_string,
    to_byte_array,
    to_compact_string,
    to_hex_string,
    to_int_array,
)

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
    result: CancelableResult = None
    connection = None
    title = None

    @staticmethod
    async def request(connection, event_number):
        EventsIO.connection = connection

        await connection.request("30{}".format(event_number))  # reminder title
        await connection.request("31{}".format(event_number))  # reminder time

        EventsIO.result = CancelableResult()
        return EventsIO.result.get_result()

    @staticmethod
    async def send_to_watch_set(message):
        def reminder_title_from_json(reminder_json):
            title_str = reminder_json.get("title")
            return to_byte_array(title_str, 18)

        def reminder_time_from_json(reminder_json):
            def create_time_detail(repeat_period, start_date, end_date, days_of_week):
                def encode_date(time_detail, start_date, end_date):
                    class Month:
                        JANUARY = 1
                        FEBRUARY = 2
                        MARCH = 3
                        APRIL = 4
                        MAY = 5
                        JUNE = 6
                        JULY = 7
                        AUGUST = 8
                        SEPTEMBER = 9
                        OCTOBER = 10
                        NOVEMBER = 11
                        DECEMBER = 12

                        def __init__(self):
                            pass

                    def string_to_month(month_str):
                        months = {
                            "january": Month.JANUARY,
                            "february": Month.FEBRUARY,
                            "march": Month.MARCH,
                            "april": Month.APRIL,
                            "may": Month.MAY,
                            "june": Month.JUNE,
                            "july": Month.JULY,
                            "august": Month.AUGUST,
                            "september": Month.SEPTEMBER,
                            "october": Month.OCTOBER,
                            "november": Month.NOVEMBER,
                            "december": Month.DECEMBER,
                        }
                        return months.get(month_str.lower(), Month.JANUARY)

                    def hex_to_dec(hex):
                        return int(str(hex), 16)

                    # take the last 2 digits only
                    time_detail[0] = hex_to_dec(start_date["year"] % 2000)
                    time_detail[1] = hex_to_dec(string_to_month(start_date["month"]))
                    time_detail[2] = hex_to_dec(start_date["day"])
                    time_detail[3] = hex_to_dec(
                        end_date["year"] % 2000
                    )  # get the last 2 gits only
                    time_detail[4] = hex_to_dec(string_to_month(end_date["month"]))
                    time_detail[5] = hex_to_dec(end_date["day"])
                    time_detail[6], time_detail[7] = 0, 0

                time_detail = [0] * 8

                if repeat_period == "NEVER":
                    encode_date(time_detail, start_date, end_date)

                elif repeat_period == "WEEKLY":
                    encode_date(time_detail, start_date, end_date)

                    day_of_week = 0
                    if days_of_week is not None:
                        for i in range(len(days_of_week)):
                            if days_of_week[i] == "SUNDAY":
                                day_of_week = day_of_week | ReminderMasks.SUNDAY_MASK
                            elif days_of_week[i] == "MONDAY":
                                day_of_week = day_of_week | ReminderMasks.MONDAY_MASK
                            elif days_of_week[i] == "TUESDAY":
                                day_of_week = day_of_week | ReminderMasks.TUESDAY_MASK
                            elif days_of_week[i] == "WEDNESDAY":
                                day_of_week = day_of_week | ReminderMasks.WEDNESDAY_MASK
                            elif days_of_week[i] == "THURSDAY":
                                day_of_week = day_of_week | ReminderMasks.THURSDAY_MASK
                            elif days_of_week[i] == "FRIDAY":
                                day_of_week = day_of_week | ReminderMasks.FRIDAY_MASK
                            elif days_of_week[i] == "SATURDAY":
                                day_of_week = day_of_week | ReminderMasks.SATURDAY_MASK

                    time_detail[6] = day_of_week
                    time_detail[7] = 0

                elif repeat_period == "MONTHLY":
                    encode_date(time_detail, start_date, end_date)

                elif repeat_period == "YEARLY":
                    encode_date(time_detail, start_date, end_date)
                else:
                    logger.debug(
                        "Cannot handle Repeat Period: {}".format(repeat_period)
                    )

                return time_detail

            def create_time_period(enabled: bool, repeat_period: str) -> int:
                time_period = 0

                if enabled:
                    time_period = time_period | ReminderMasks.ENABLED_MASK
                if repeat_period == "WEEKLY":
                    time_period = time_period | ReminderMasks.WEEKLY_MASK
                elif repeat_period == "MONTHLY":
                    time_period = time_period | ReminderMasks.MONTHLY_MASK
                elif repeat_period == "YEARLY":
                    time_period = time_period | ReminderMasks.YEARLY_MASK
                return time_period

            enabled = reminder_json.get("enabled")
            repeat_period = reminder_json.get("repeat_period")
            start_date = reminder_json.get("start_date")
            end_date = reminder_json.get("end_date")
            days_of_week = reminder_json.get("days_of_week")

            reminder_cmd = bytearray()

            reminder_cmd += bytearray([create_time_period(enabled, repeat_period)])
            reminder_cmd += bytearray(
                create_time_detail(repeat_period, start_date, end_date, days_of_week)
            )

            return reminder_cmd

        reminders_json_arr = json.loads(message).get("value")
        for index, element in enumerate(reminders_json_arr):
            reminder_json = element
            title = reminder_title_from_json(reminder_json)

            title_byte_arr = bytearray([CHARACTERISTICS["CASIO_REMINDER_TITLE"]])
            title_byte_arr += bytearray([index + 1])
            title_byte_arr += title
            title_byte_arr_to_send = to_compact_string(to_hex_string(title_byte_arr))
            await EventsIO.connection.write(0x000E, title_byte_arr_to_send)

            reminder_time_byte_arr = bytearray([])
            reminder_time_byte_arr += bytearray(
                [CHARACTERISTICS["CASIO_REMINDER_TIME"]]
            )
            reminder_time_byte_arr += bytearray([index + 1])
            reminder_time_byte_arr += reminder_time_from_json(reminder_json.get("time"))
            reminder_time_byte_arr_to_send = to_compact_string(
                to_hex_string(bytearray(reminder_time_byte_arr))
            )
            await EventsIO.connection.write(0x000E, reminder_time_byte_arr_to_send)

    @staticmethod
    def on_received(message):
        data = to_hex_string(message)

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

            int_arr = to_int_array(reminder_str)
            if int_arr[3] == 0xFF:
                # 0XFF indicates end of reminders
                return json.dumps({"end": ""})

            reminder_all = to_int_array(reminder_str)
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

        reminder_json = json.loads(reminder_time_to_json(data[2:]))
        reminder_json.update(EventsIO.title)
        EventsIO.result.set_result(reminder_json)

    @staticmethod
    def on_received_title(message):
        EventsIO.title = ReminderDecoder.reminder_title_to_json(message)


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
