import json
import datetime
import logging
from settings import settings
from utils import (
    to_int_array,
    to_compact_string,
    to_hex_string,
    clean_str,
    to_ascii_string,
    to_byte_array,
    dec_to_hex,
)
from casio_constants import CasioConstants
from enum import IntEnum
from alarms import alarmsInst, alarmDecoder

logger = logging.getLogger(__name__)

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class WatchButton(IntEnum):
    UPPER_LEFT = 1
    LOWER_LEFT = 2
    UPPER_RIGHT = 3
    LOWER_RIGHT = 4
    NO_BUTTON = 5
    INVALID = 6


class DtsState(IntEnum):
    ZERO = 0
    TWO = 2
    FOUR = 4


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


class SettingsDecoder:
    def to_json_time_adjustment(settings):
        return {"timeAdjustment": settings.time_adjustment}


class ReminderDecoder:
    def reminder_title_to_json(title_byte: str) -> dict:
        int_arr = to_int_array(title_byte)
        if int_arr[2] == 0xFF:
            # 0XFF indicates end of reminders
            return {"end": ""}
        reminder_json = {}

        reminder_json["title"] = clean_str(to_ascii_string(title_byte, 2))
        return reminder_json


def create_key(data):
    short_str = to_compact_string(data)
    key_length = 2
    # get the first byte of the returned data, which indicates the data content.
    start_of_data = short_str[0:2].upper()
    if start_of_data in ["1D", "1E", "1F", "30", "31"]:
        key_length = 4
    key = short_str[0:key_length].upper()
    return key


def to_json(_data):
    data = to_hex_string(_data)
    int_array = to_int_array(data)
    json_obj = {}
    if int_array[0] == CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]:
        return {
            "ALARMS": {
                "value": alarmDecoder.toJson(data)["ALARMS"],
                "key": "GET_ALARMS",
            }
        }

    if int_array[0] == CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]:
        return {
            "ALARMS2": {
                "value": alarmDecoder.toJson(data)["ALARMS"],
                "key": "GET_ALARMS2",
            }
        }

    # Add topics so the right component will receive data
    elif int_array[0] == CHARACTERISTICS["CASIO_DST_SETTING"]:
        data_json = {"key": create_key(data), "value": data}
        json_obj["CASIO_DST_SETTING"] = data_json

    elif int_array[0] == CHARACTERISTICS["CASIO_SETTING_FOR_BASIC"]:

        def create_json_settings(setting_string):
            mask_24_hours = 0b00000001
            MASK_BUTTON_TONE_OFF = 0b00000010
            MASK_LIGHT_OFF = 0b00000100
            POWER_SAVING_MODE = 0b00010000

            setting_array = to_int_array(setting_string)

            if setting_array[1] & mask_24_hours != 0:
                settings.time_format = "24h"
            else:
                settings.time_format = "12h"
            settings.button_tone = setting_array[1] & MASK_BUTTON_TONE_OFF == 0
            settings.auto_light = setting_array[1] & MASK_LIGHT_OFF == 0
            settings.power_saving_mode = setting_array[1] & POWER_SAVING_MODE == 0

            if setting_array[4] == 1:
                settings.date_format = "DD:MM"
            else:
                settings.date_format = "MM:DD"

            if setting_array[5] == 0:
                settings.language = "English"
            if setting_array[5] == 1:
                settings.language = "Spanish"
            if setting_array[5] == 2:
                settings.language = "French"
            if setting_array[5] == 3:
                settings.language = "German"
            if setting_array[5] == 4:
                settings.language = "Italian"
            if setting_array[5] == 5:
                settings.language = "Russian"

            if setting_array[2] == 1:
                settings.light_duration = "4s"
            else:
                settings.light_duration = "2s"

            return json.dumps(settings.__dict__)

        data_json = {"key": create_key(data), "value": create_json_settings(data)}
        settings_json = {"SETTINGS": data_json}
        return settings_json

    elif int_array[0] == CHARACTERISTICS["CASIO_SETTING_FOR_BLE"]:
        settings.CasioIsAutoTimeOriginalValue = data
        value_json = SettingsDecoder.to_json_time_adjustment(settings)
        data_json = {"key": create_key(data), "value": value_json}
        return {"TIME_ADJUSTMENT": data_json}

    elif int_array[0] == CHARACTERISTICS["CASIO_REMINDER_TIME"]:
        reminder_json = {}

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

            short_str = to_compact_string(reminder_str)
            # get the first byte of the returned data, which indicates the data content.
            key = short_str[:4].upper()

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

        value = reminder_time_to_json(data[2:])
        reminder_json["REMINDERS"] = {
            "key": create_key(data),
            "value": json.loads(value),
        }
        return reminder_json

    elif int_array[0] == CHARACTERISTICS["CASIO_REMINDER_TITLE"]:
        return {
            "REMINDERS": {
                "key": create_key(data),
                "value": ReminderDecoder.reminder_title_to_json(data),
            }
        }
    elif int_array[0] == CHARACTERISTICS["CASIO_TIMER"]:
        data_json = {"key": create_key(data), "value": data}
        json_obj["CASIO_TIMER"] = data_json

    elif int_array[0] == CHARACTERISTICS["CASIO_WORLD_CITIES"]:
        data_json = {"key": create_key(data), "value": data}
        characteristics_array = to_int_array(data)
        json_obj["CASIO_WORLD_CITIES"] = data_json
    elif int_array[0] == CHARACTERISTICS["CASIO_DST_WATCH_STATE"]:
        data_json = {"key": create_key(data), "value": data}
        json_obj["CASIO_DST_WATCH_STATE"] = data_json
    elif int_array[0] == CHARACTERISTICS["CASIO_WATCH_NAME"]:
        data_json = {"key": create_key(data), "value": data}
        json_obj["CASIO_WATCH_NAME"] = data_json
    elif int_array[0] == CHARACTERISTICS["CASIO_WATCH_CONDITION"]:
        data_json = {"key": create_key(data), "value": data}
        json_obj["CASIO_WATCH_CONDITION"] = data_json
    elif int_array[0] == CHARACTERISTICS["CASIO_APP_INFORMATION"]:
        data_json = {"key": create_key(data), "value": data}
        json_obj["CASIO_APP_INFORMATION"] = data_json
    elif int_array[0] == CHARACTERISTICS["CASIO_BLE_FEATURES"]:
        data_json = {"key": create_key(data), "value": data}
        json_obj["BUTTON_PRESSED"] = data_json
    return json_obj


async def callWriter(connection, message: str):
    print(message)
    action_json = json.loads(message)
    action = action_json.get("action")
    match action:
        case "GET_ALARMS":
            alarm_command = to_compact_string(
                to_hex_string(bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]]))
            )

            await connection.write(0x000C, alarm_command)

        case "GET_ALARMS2":
            # get the rest of the alarms
            alarm_command2 = to_compact_string(
                to_hex_string(bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]]))
            )
            await connection.write(0x000C, alarm_command2)

        case "SET_ALARMS":
            alarms_json_arr = json.loads(message).get("value")
            alarm_casio0 = to_compact_string(
                to_hex_string(
                    alarmsInst.from_json_alarm_first_alarm(alarms_json_arr[0])
                )
            )
            await connection.write(0x000E, alarm_casio0)
            alarm_casio = to_compact_string(
                to_hex_string(alarmsInst.fromJsonAlarmSecondaryAlarms(alarms_json_arr))
            )
            await connection.write(0x000E, alarm_casio)

        case "SET_REMINDERS":

            def reminder_title_from_json(reminder_json):
                title_str = reminder_json.get("title")
                return to_byte_array(title_str, 18)

            def reminder_time_from_json(reminder_json):
                def create_time_detail(
                    repeat_period, start_date, end_date, days_of_week
                ):
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
                        time_detail[1] = hex_to_dec(
                            string_to_month(start_date["month"])
                        )
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
                                    day_of_week = (
                                        day_of_week | ReminderMasks.SUNDAY_MASK
                                    )
                                elif days_of_week[i] == "MONDAY":
                                    day_of_week = (
                                        day_of_week | ReminderMasks.MONDAY_MASK
                                    )
                                elif days_of_week[i] == "TUESDAY":
                                    day_of_week = (
                                        day_of_week | ReminderMasks.TUESDAY_MASK
                                    )
                                elif days_of_week[i] == "WEDNESDAY":
                                    day_of_week = (
                                        day_of_week | ReminderMasks.WEDNESDAY_MASK
                                    )
                                elif days_of_week[i] == "THURSDAY":
                                    day_of_week = (
                                        day_of_week | ReminderMasks.THURSDAY_MASK
                                    )
                                elif days_of_week[i] == "FRIDAY":
                                    day_of_week = (
                                        day_of_week | ReminderMasks.FRIDAY_MASK
                                    )
                                elif days_of_week[i] == "SATURDAY":
                                    day_of_week = (
                                        day_of_week | ReminderMasks.SATURDAY_MASK
                                    )

                        time_detail[6] = day_of_week
                        time_detail[7] = 0

                    elif repeat_period == "MONTHLY":
                        encode_date(time_detail, start_date, end_date)

                    elif repeat_period == "YEARLY":
                        encode_date(time_detail, start_date, end_date)
                    else:
                        logger.info(
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
                    create_time_detail(
                        repeat_period, start_date, end_date, days_of_week
                    )
                )

                return reminder_cmd

            reminders_json_arr = json.loads(message).get("value")
            for index, element in enumerate(reminders_json_arr):
                reminder_json = element
                title = reminder_title_from_json(reminder_json)

                title_byte_arr = bytearray([CHARACTERISTICS["CASIO_REMINDER_TITLE"]])
                title_byte_arr += bytearray([index + 1])
                title_byte_arr += title
                title_byte_arr_to_send = to_compact_string(
                    to_hex_string(title_byte_arr)
                )
                await connection.write(0x000E, title_byte_arr_to_send)

                reminder_time_byte_arr = bytearray([])
                reminder_time_byte_arr += bytearray(
                    [CHARACTERISTICS["CASIO_REMINDER_TIME"]]
                )
                reminder_time_byte_arr += bytearray([index + 1])
                reminder_time_byte_arr += reminder_time_from_json(reminder_json)
                reminder_time_byte_arr_to_send = to_compact_string(
                    to_hex_string(bytearray(reminder_time_byte_arr))
                )
                logger.error(reminder_time_byte_arr_to_send)
                await connection.write(0x000E, reminder_time_byte_arr_to_send)

        case "GET_SETTINGS":
            await connection.write(
                0x000C, bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_BASIC"]])
            )

        case "SET_SETTINGS":

            def encode(settings: dict):
                mask_24_hours = 0b00000001
                MASK_BUTTON_TONE_OFF = 0b00000010
                MASK_LIGHT_OFF = 0b00000100
                POWER_SAVING_MODE = 0b00010000

                arr = bytearray(12)
                arr[0] = CHARACTERISTICS["CASIO_SETTING_FOR_BASIC"]
                if settings.time_format == "24h":
                    arr[1] = arr[1] | mask_24_hours
                if not settings.button_tone:
                    arr[1] = arr[1] | MASK_BUTTON_TONE_OFF
                if not settings.auto_light:
                    arr[1] = arr[1] | MASK_LIGHT_OFF
                if not settings.power_saving_mode:
                    arr[1] = arr[1] | POWER_SAVING_MODE

                if settings.light_duration == "4s":
                    arr[2] = 1
                if settings.date_format == "DD:MM":
                    arr[4] = 1

                language_index = {
                    "English": 0,
                    "Spanish": 1,
                    "French": 2,
                    "German": 3,
                    "Italian": 4,
                    "Russian": 5,
                }
                arr[5] = language_index.get(settings.language, 0)

                return arr

            encoded_settings = encode(settings)
            await connection.write(
                0x000E, to_compact_string(to_hex_string(encoded_settings))
            )

        case "GET_TIME_ADJUSTMENT":
            await connection.write(
                0x000C,
                to_compact_string(
                    to_hex_string(bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_BLE"]]))
                ),
            )

        case "SET_TIME_ADJUSTMENT":
            value = json.loads(message).get("value")

            def encode_time_adjustment(time_adjustment):
                raw_string = settings.CasioIsAutoTimeOriginalValue
                int_array = to_int_array(raw_string)

                int_array[12] = 0x80 if time_adjustment == "True" else 0x00
                return bytes(int_array)

            encoded_time_adj = encode_time_adjustment(value)
            write_cmd = to_compact_string(to_hex_string(encoded_time_adj))
            await connection.write(0x000E, write_cmd)

        case "GET_TIMER":
            connection.write(0x000C, bytearray([CHARACTERISTICS["CASIO_TIMER"]]))

        case "SET_TIMER":
            seconds = json.loads(message).get("value")

            def encode(seconds_str):
                in_seconds = int(seconds_str)
                hours = in_seconds // 3600
                minutes_and_seconds = in_seconds % 3600
                minutes = minutes_and_seconds // 60
                seconds = minutes_and_seconds % 60

                arr = bytearray(7)
                arr[0] = 0x18
                arr[1] = hours
                arr[2] = minutes
                arr[3] = seconds
                return arr

            seconds_as_byte_arr = encode(seconds)
            seconds_as_compact_str = to_compact_string(
                to_hex_string(seconds_as_byte_arr)
            )
            await connection.write(0x000E, seconds_as_compact_str)

        case "SET_TIME":
            date_time_ms = int(json.loads(message).get("value"))
            print("date_time_ms: {}".format(date_time_ms))
            date_time = datetime.datetime.fromtimestamp(date_time_ms / 1000.0)
            time_data = TimeEncoder.prepare_current_time(date_time)
            time_command = to_hex_string(
                bytearray([CHARACTERISTICS["CASIO_CURRENT_TIME"]]) + time_data
            )
            await connection.write(0xE, to_compact_string(time_command))

        case _:
            print("callWriter: Unhandled command", action)


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
