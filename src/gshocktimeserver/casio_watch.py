import json
import datetime
import logging
from utils import to_int_array, to_compact_string, to_hex_string, clean_str, to_ascii_string, to_byte_array, dec_to_hex
from casio_constants import CasioConstants
from enum import IntEnum
from alarms import alarmsInst, alarmDecoder

logger = logging.getLogger(__name__)

CHARACTERISTICS = CasioConstants.CHARACTERISTICS


class WATCH_BUTTON(IntEnum):
    UPPER_LEFT = 1
    LOWER_LEFT = 2
    UPPER_RIGHT = 3
    LOWER_RIGHT = 4
    NO_BUTTON = 5
    INVALID = 6


class DTS_STATE(IntEnum):
    ZERO = 0
    TWO = 2
    FOUR = 4


class Settings:
    time_format = ""
    date_format = ""
    language = ""
    auto_light = False
    light_duration = ""
    power_saving_mode = False
    button_tone = True
    time_adjustment = True


settings = Settings()


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
        return {'timeAdjustment': settings.time_adjustment}


class ReminderDecoder:
    def reminder_title_to_json(titleByte: str) -> dict:
        intArr = to_int_array(titleByte)
        if intArr[2] == 0xFF:
            # 0XFF indicates end of reminders
            return {'end': ''}
        reminderJson = {}

        reminderJson['title'] = clean_str(to_ascii_string(titleByte, 2))
        return reminderJson


def create_key(data):
    shortStr = to_compact_string(data)
    keyLength = 2
    # get the first byte of the returned data, which indicates the data content.
    startOfData = shortStr[0:2].upper()
    if startOfData in ["1D", "1E", "1F", "30", "31"]:
        keyLength = 4
    key = shortStr[0:keyLength].upper()
    return key


def to_json(_data):
    data = to_hex_string(_data)
    int_array = to_int_array(data)
    json_obj = {}
    if int_array[0] == CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]:
        return {"ALARMS": {"value": alarmDecoder.toJson(data)["ALARMS"],
                           "key": "GET_ALARMS"}}

    if int_array[0] == CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]:
        return {"ALARMS2": {"value": alarmDecoder.toJson(data)["ALARMS"],
                            "key": "GET_ALARMS2"}}

    # Add topics so the right component will receive data
    elif int_array[0] == CHARACTERISTICS["CASIO_DST_SETTING"]:
        data_json = {"key": create_key(data), "value": data}
        json_obj["CASIO_DST_SETTING"] = data_json

    elif int_array[0] == CHARACTERISTICS["CASIO_SETTING_FOR_BASIC"]:

        def create_json_settings(setting_string):
            MASK_24_HOURS = 0b00000001
            MASK_BUTTON_TONE_OFF = 0b00000010
            MASK_LIGHT_OFF = 0b00000100
            POWER_SAVING_MODE = 0b00010000

            # settings = Settings()

            setting_array = to_int_array(setting_string)

            if setting_array[1] & MASK_24_HOURS != 0:
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

            def convert_array_list_to_json_array(arrayList):
                jsonArray = []
                for item in arrayList:
                    jsonArray.append(item)

                return jsonArray

            def decode_time_period(timePeriod: int) -> tuple:

                enabled = False
                repeatPeriod = ""

                if timePeriod & ReminderMasks.ENABLED_MASK == ReminderMasks.ENABLED_MASK:
                    enabled = True

                if timePeriod & ReminderMasks.WEEKLY_MASK == ReminderMasks.WEEKLY_MASK:
                    repeatPeriod = "WEEKLY"
                elif timePeriod & ReminderMasks.MONTHLY_MASK == ReminderMasks.MONTHLY_MASK:
                    repeatPeriod = "MONTHLY"
                elif timePeriod & ReminderMasks.YEARLY_MASK == ReminderMasks.YEARLY_MASK:
                    repeatPeriod = "YEARLY"
                else:
                    repeatPeriod = "NEVER"

                return (enabled, repeatPeriod)

            def decode_time_detail(timeDetail):

                def decodeDate(timeDetail):

                    def intToMonthStr(monthInt):
                        if monthInt == 1:
                            return "JANUARY"
                        elif monthInt == 2:
                            return "FEBRUARY"
                        elif monthInt == 3:
                            return "MARCH"
                        elif monthInt == 4:
                            return "APRIL"
                        elif monthInt == 5:
                            return "MAY"
                        elif monthInt == 6:
                            return "JUNE"
                        elif monthInt == 7:
                            return "JULY"
                        elif monthInt == 8:
                            return "AUGUST"
                        elif monthInt == 9:
                            return "SEPTEMBER"
                        elif monthInt == 10:
                            return "OCTOBER"
                        elif monthInt == 11:
                            return "NOVEMBER"
                        elif monthInt == 12:
                            return "DECEMBER"
                        else:
                            return ""

                    date = json.loads("{}")

                    date["year"] = dec_to_hex(timeDetail[0]) + 2000
                    date["month"] = intToMonthStr(dec_to_hex(timeDetail[1]))
                    date["day"] = dec_to_hex(timeDetail[2])

                    return date

                result = {}

                #                  00 23 02 21 23 02 21 00 00
                # start from here:    ^
                # so, skip 1
                startDate = decodeDate(timeDetail[1:])

                result["startDate"] = startDate

                #                  00 23 02 21 23 02 21 00 00
                # start from here:             ^
                # so, skip 4
                endDate = decodeDate(timeDetail[4:])

                result["endDate"] = endDate

                dayOfWeek = timeDetail[7]
                daysOfWeek = []
                if (dayOfWeek & ReminderMasks.SUNDAY_MASK == ReminderMasks.SUNDAY_MASK):
                    daysOfWeek.append("SUNDAY")
                if (dayOfWeek & ReminderMasks.MONDAY_MASK == ReminderMasks.MONDAY_MASK):
                    daysOfWeek.append("MONDAY")
                if (dayOfWeek & ReminderMasks.TUESDAY_MASK == ReminderMasks.TUESDAY_MASK):
                    daysOfWeek.append("TUESDAY")
                if (dayOfWeek & ReminderMasks.WEDNESDAY_MASK ==
                        ReminderMasks.WEDNESDAY_MASK):
                    daysOfWeek.append("WEDNESDAY")
                if (dayOfWeek & ReminderMasks.THURSDAY_MASK == ReminderMasks.THURSDAY_MASK):
                    daysOfWeek.append("THURSDAY")
                if (dayOfWeek & ReminderMasks.FRIDAY_MASK == ReminderMasks.FRIDAY_MASK):
                    daysOfWeek.append("FRIDAY")
                if (dayOfWeek & ReminderMasks.SATURDAY_MASK == ReminderMasks.SATURDAY_MASK):
                    daysOfWeek.append("SATURDAY")
                result["daysOfWeek"] = daysOfWeek
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
            reminder_json["repeatPeriod"] = time_period[1]

            time_detail_map = decode_time_detail(reminder)

            reminder_json["startDate"] = time_detail_map["startDate"]
            reminder_json["endDate"] = time_detail_map["endDate"]
            reminder_json["daysOfWeek"] = convert_array_list_to_json_array(
                time_detail_map["daysOfWeek"])

            return json.dumps({"time": reminder_json})

        value = reminder_time_to_json(data[2:])
        reminder_json["REMINDERS"] = {
            "key": create_key(data),
            "value": json.loads(value)}
        return reminder_json

    elif int_array[0] == CHARACTERISTICS["CASIO_REMINDER_TITLE"]:
        return {"REMINDERS": {"key": create_key(data),
                              "value": ReminderDecoder.reminder_title_to_json(data)}}
    elif int_array[0] == CHARACTERISTICS["CASIO_TIMER"]:
        data_json = {"key": create_key(data), "value": data}
        json_obj["CASIO_TIMER"] = data_json

    elif int_array[0] == CHARACTERISTICS["CASIO_WORLD_CITIES"]:
        data_json = {"key": create_key(data), "value": data}
        characteristics_array = to_int_array(data)
        # if characteristics_array[1] == 0:
        #     # 0x1F 00 ... Only the first World City contains the home time.
        #     # Send this data on topic "HOME_TIME" to be received by HomeTime custom component.
        #     json["HOME_TIME"] = data_json
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
        dataJson = {"key": create_key(data), "value": data}
        json_obj["CASIO_APP_INFORMATION"] = dataJson
    elif int_array[0] == CHARACTERISTICS["CASIO_BLE_FEATURES"]:
        dataJson = {"key": create_key(data), "value": data}
        json_obj["BUTTON_PRESSED"] = dataJson
    return json_obj


async def callWriter(connection, message: str):
    print(message)
    actionJson = json.loads(message)
    action = actionJson.get("action")
    match action:
        case "GET_ALARMS":
            alarm_command = to_compact_string(to_hex_string(
                bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_ALM"]])))

            await connection.write(
                0x000c,
                alarm_command)

        case "GET_ALARMS2":
            # get the rest of the alarms
            alarm_command2 = to_compact_string(to_hex_string(
                bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_ALM2"]])))
            await connection.write(
                0x000c,
                alarm_command2)

        case "SET_ALARMS":
            alarmsJsonArr = json.loads(message).get("value")
            alarmCasio0 = to_compact_string(
                to_hex_string(
                    alarmsInst.fromJsonAlarmFirstAlarm(
                        alarmsJsonArr[0])))
            await connection.write(0x000e, alarmCasio0)
            alarmCasio = to_compact_string(to_hex_string(
                alarmsInst.fromJsonAlarmSecondaryAlarms(alarmsJsonArr)))
            await connection.write(0x000e, alarmCasio)

        case "SET_REMINDERS":

            def reminderTitleFromJson(reminderJson):
                titleStr = reminderJson.get("title")
                return to_byte_array(titleStr, 18)

            def reminderTimeFromJson(reminderJson):

                def createTimeDetail(repeatPeriod, startDate, endDate, daysOfWeek):

                    def encodeDate(timeDetail, startDate, endDate):

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

                        def stringToMonth(monthStr):
                            monthStr = monthStr.lower()
                            if monthStr == "january":
                                return Month.JANUARY
                            elif monthStr == "february":
                                return Month.FEBRUARY
                            elif monthStr == "march":
                                return Month.MARCH
                            elif monthStr == "april":
                                return Month.APRIL
                            elif monthStr == "may":
                                return Month.MAY
                            elif monthStr == "june":
                                return Month.JUNE
                            elif monthStr == "july":
                                return Month.JULY
                            elif monthStr == "august":
                                return Month.AUGUST
                            elif monthStr == "september":
                                return Month.SEPTEMBER
                            elif monthStr == "october":
                                return Month.OCTOBER
                            elif monthStr == "november":
                                return Month.NOVEMBER
                            elif monthStr == "december":
                                return Month.DECEMBER
                            else:
                                return Month.JANUARY

                        def hex_to_dec(hex):
                            return int(str(hex), 16)

                        # take the last 2 digits only
                        timeDetail[0] = hex_to_dec(startDate['year'] % 2000)
                        timeDetail[1] = hex_to_dec(stringToMonth(startDate['month']))
                        timeDetail[2] = hex_to_dec(startDate['day'])

                        timeDetail[3] = hex_to_dec(
                            endDate['year'] % 2000)  # get the last 2 gits only
                        timeDetail[4] = hex_to_dec(stringToMonth(endDate['month']))
                        timeDetail[5] = hex_to_dec(endDate['day'])

                        timeDetail[6] = 0
                        timeDetail[7] = 0

                    timeDetail = [0] * 8

                    if repeatPeriod == "NEVER":
                        encodeDate(timeDetail, startDate, endDate)

                    elif repeatPeriod == "WEEKLY":
                        encodeDate(timeDetail, startDate, endDate)

                        dayOfWeek = 0
                        if daysOfWeek is not None:
                            for i in range(len(daysOfWeek)):
                                if daysOfWeek[i] == "SUNDAY":
                                    dayOfWeek = dayOfWeek | ReminderMasks.SUNDAY_MASK
                                elif daysOfWeek[i] == "MONDAY":
                                    dayOfWeek = dayOfWeek | ReminderMasks.MONDAY_MASK
                                elif daysOfWeek[i] == "TUESDAY":
                                    dayOfWeek = dayOfWeek | ReminderMasks.TUESDAY_MASK
                                elif daysOfWeek[i] == "WEDNESDAY":
                                    dayOfWeek = dayOfWeek | ReminderMasks.WEDNESDAY_MASK
                                elif daysOfWeek[i] == "THURSDAY":
                                    dayOfWeek = dayOfWeek | ReminderMasks.THURSDAY_MASK
                                elif daysOfWeek[i] == "FRIDAY":
                                    dayOfWeek = dayOfWeek | ReminderMasks.FRIDAY_MASK
                                elif daysOfWeek[i] == "SATURDAY":
                                    dayOfWeek = dayOfWeek | ReminderMasks.SATURDAY_MASK

                        timeDetail[6] = dayOfWeek
                        timeDetail[7] = 0

                    elif repeatPeriod == "MONTHLY":
                        encodeDate(timeDetail, startDate, endDate)

                    elif repeatPeriod == "YEARLY":
                        encodeDate(timeDetail, startDate, endDate)
                    else:
                        logger.info(
                            "Cannot handle Repeat Period: {}".format(repeatPeriod))

                    return timeDetail

                def createTimePeriod(enabled: bool, repeatPeriod: str) -> int:
                    timePeriod = 0

                    if enabled:
                        timePeriod = timePeriod | ReminderMasks.ENABLED_MASK
                    if repeatPeriod == "WEEKLY":
                        timePeriod = timePeriod | ReminderMasks.WEEKLY_MASK
                    elif repeatPeriod == "MONTHLY":
                        timePeriod = timePeriod | ReminderMasks.MONTHLY_MASK
                    elif repeatPeriod == "YEARLY":
                        timePeriod = timePeriod | ReminderMasks.YEARLY_MASK
                    return timePeriod

                enabled = reminderJson.get("enabled")
                repeatPeriod = reminderJson.get("repeatPeriod")
                startDate = reminderJson.get("startDate")
                endDate = reminderJson.get("endDate")
                daysOfWeek = reminderJson.get("daysOfWeek")

                reminderCmd = bytearray()

                reminderCmd += bytearray([createTimePeriod(enabled, repeatPeriod)])
                reminderCmd += bytearray(createTimeDetail(repeatPeriod,
                                         startDate, endDate, daysOfWeek))

                return reminderCmd

            remindersJsonArr = json.loads(message).get("value")
            for index, element in enumerate(remindersJsonArr):
                reminderJson = element
                title = reminderTitleFromJson(reminderJson)

                title_byte_arr = bytearray([CHARACTERISTICS["CASIO_REMINDER_TITLE"]])
                title_byte_arr += bytearray([index + 1])
                title_byte_arr += title
                title_byte_arr_to_send = to_compact_string(
                    to_hex_string(title_byte_arr))
                await connection.write(0x000e, title_byte_arr_to_send)

                reminder_time_byte_arr = bytearray([])
                reminder_time_byte_arr += bytearray(
                    [CHARACTERISTICS["CASIO_REMINDER_TIME"]])
                reminder_time_byte_arr += bytearray([index + 1])
                reminder_time_byte_arr += reminderTimeFromJson(reminderJson)
                reminder_time_byte_arr_to_send = to_compact_string(
                    to_hex_string(bytearray(reminder_time_byte_arr)))
                logger.error(reminder_time_byte_arr_to_send)
                await connection.write(0x000e, reminder_time_byte_arr_to_send)

        case "GET_SETTINGS":
            await connection.write(0x000c, bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_BASIC"]]))

        case "SET_SETTINGS":
            # settings = json.loads(message).get("value")

            def encode(settings: dict):
                MASK_24_HOURS = 0b00000001
                MASK_BUTTON_TONE_OFF = 0b00000010
                MASK_LIGHT_OFF = 0b00000100
                POWER_SAVING_MODE = 0b00010000

                arr = bytearray(12)
                arr[0] = CHARACTERISTICS["CASIO_SETTING_FOR_BASIC"]
                if settings.time_format == "24h":
                    arr[1] = (arr[1] | MASK_24_HOURS)
                if not settings.button_tone:
                    arr[1] = (arr[1] | MASK_BUTTON_TONE_OFF)
                if not settings.auto_light:
                    arr[1] = (arr[1] | MASK_LIGHT_OFF)
                if not settings.power_saving_mode:
                    arr[1] = (arr[1] | POWER_SAVING_MODE)

                if settings.light_duration == "4s":
                    arr[2] = 1
                if settings.date_format == "DD:MM":
                    arr[4] = 1

                language = settings.language
                if language == 'English':
                    arr[5] = 0
                elif language == 'Spanish':
                    arr[5] = 1
                elif language == 'French':
                    arr[5] = 2
                elif language == 'German':
                    arr[5] = 3
                elif language == 'Italian':
                    arr[5] = 4
                elif language == 'Russian':
                    arr[5] = 5

                return arr

            encoded_settings = encode(settings)
            await connection.write(0x000e, to_compact_string(to_hex_string(encoded_settings)))

        case "GET_TIME_ADJUSTMENT":
            await connection.write(0x000c, to_compact_string(to_hex_string(bytearray([CHARACTERISTICS["CASIO_SETTING_FOR_BLE"]]))))

        case "SET_TIME_ADJUSTMENT":
            value = json.loads(message).get("value")

            def encodeTimeAdjustment(timeAdjustment):
                raw_string = settings.CasioIsAutoTimeOriginalValue
                intArray = to_int_array(raw_string)

                intArray[12] = 0x80 if timeAdjustment == 'True' else 0x00
                return bytes(intArray)

            encodedTimeAdj = encodeTimeAdjustment(value)
            write_cmd = to_compact_string(to_hex_string(encodedTimeAdj))
            await connection.write(0x000e, write_cmd)

        case "GET_TIMER":
            connection.write(0x000c, bytearray([CHARACTERISTICS["CASIO_TIMER"]]))

        case "SET_TIMER":
            seconds = json.loads(message).get("value")

            def encode(secondsStr):
                inSeconds = int(secondsStr)
                hours = inSeconds // 3600
                minutesAndSeconds = inSeconds % 3600
                minutes = minutesAndSeconds // 60
                seconds = minutesAndSeconds % 60

                arr = bytearray(7)
                arr[0] = 0x18
                arr[1] = hours
                arr[2] = minutes
                arr[3] = seconds
                return arr

            seconds_as_byte_arr = encode(seconds)
            seconds_as_compact_str = to_compact_string(
                to_hex_string(seconds_as_byte_arr))
            await connection.write(0x000e, seconds_as_compact_str)

        case "SET_TIME":
            dateTimeMs = int(json.loads(message).get("value"))
            print("dateTimeMs: {}".format(dateTimeMs))
            dateTime = datetime.datetime.fromtimestamp(dateTimeMs / 1000.0)
            timeData = TimeEncoder.prepare_current_time(dateTime)
            timeCommand = to_hex_string(
                bytearray([CHARACTERISTICS["CASIO_CURRENT_TIME"]]) + timeData)
            await connection.write(0xe, to_compact_string(timeCommand))

        case _:
            print("callWriter: Unhandled command", action)


class TimeEncoder():
    def prepare_current_time(date: datetime.datetime):
        arr = bytearray(10)
        year = date.year
        arr[0] = (year >> 0 & 0xff)
        arr[1] = (year >> 8 & 0xff)
        arr[2] = date.month
        arr[3] = date.day
        arr[4] = date.hour
        arr[5] = date.minute
        arr[6] = date.second
        arr[7] = date.weekday()
        arr[8] = 0
        arr[9] = 1
        return arr
