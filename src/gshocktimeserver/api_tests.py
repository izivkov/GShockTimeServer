import calendar
import json
import pytz
import time
from datetime import datetime, timezone

from connection import Connection
from gshock_api import GshockAPI
from casio_watch import DtsState, settings
from event import Event, create_event_date, RepeatPeriod
from scanner import scanner
from logger import logger


def prompt():
    print("========================================================================")
    print("Press and hold lower-left button on your watch for 3 seconds to start...")
    print("========================================================================")
    print("")


async def run_api_tests():
    prompt()

    device = await scanner.scan()
    logger.debug("Found: {}".format(device))

    connection = Connection(device)
    await connection.connect()

    api = GshockAPI(connection)

    # await api.get_app_info()

    # pressed_button = await api.get_pressed_button()
    # logger.debug("pressed button: {}".format(pressed_button))

    # watch_name = await api.get_watch_name()
    # print("got watch name: {}".format(watch_name))

    # world_city = await api.get_dst_for_world_cities(0)
    # print("world city: {}".format(world_city))

    # world_city = await api.get_dst_for_world_cities(1)
    # print("world city: {}".format(world_city))

    # dst_state = await api.get_dst_watch_state(DtsState.ZERO)
    # print("dst_state: {}".format(dst_state))

    # dst_state = await api.get_dst_watch_state(DtsState.TWO)
    # print("dst_state: {}".format(dst_state))

    await api.set_time()
    # You can also set arbitrasy time like this:
    # time_string = "10:10:30"
    # seconds = convert_time_string_to_epoch(time_string)
    # await api.set_time(seconds)

    # alarms = await api.get_alarms()
    # print("alarms: {}".format(alarms))

    # alarms[3]["enabled"] = True
    # alarms[3]["hour"] = 7
    # alarms[3]["minute"] = 25
    # alarms[3]["enabled"] = False

    # await api.set_alarms(alarms)

    # alarms = await api.get_alarms()
    # print("After Setting: alarms: {}".format(alarms))

    # seconds = await api.get_timer()
    # print("timer: {} seconds".format(seconds))

    # await api.set_timer(235)
    # seconds = await api.get_timer()
    # print("timer: {} after setting seconds".format(seconds))

    # # await api.set_timer(seconds + 10)
    # time_adjstment = await api.get_time_adjustment()
    # logger.debug("time_adjstment: {}".format(time_adjstment))

    # settings.timeAdjustment = True
    # await api.set_time_adjustment(settings)

    # settings_local = await api.get_basic_settings()
    # logger.debug("settings: {}".format(settings_local))

    # settings_local["button_tone"] = True
    # settings_local["language"] = "Engish"
    # settings_local["time_format"] = "12h"

    # await api.set_settings(settings_local)

    # Create a single event
    # tz = pytz.timezone("America/Toronto")
    # dt = datetime.now(timezone.utc)
    # utc_timestamp = dt.timestamp()
    # event_date = create_event_date(utc_timestamp, tz)
    # event_date_str = json.dumps(event_date.__dict__)
    # event_json_str = (
    #     """{"title":"Test Event", "time":{"selected":\""""
    #     + str(False)
    #     + """\", "enabled":\""""
    #     + str(True)
    #     + """\", "repeat_period":\""""
    #     + RepeatPeriod.WEEKLY
    #     + """\","days_of_week":\""""
    #     + "MONDAY"
    #     + """\", "start_date":"""
    #     + event_date_str
    #     + """, "end_date":"""
    #     + event_date_str
    #     + """}}"""
    # )
    # Event().create_event(json.loads(event_json_str))

    # reminders = await api.get_reminders()
    # for reminder in reminders:
    #     logger.debug("reminder: {}".format(reminder.__str__()))

    # await api.set_reminders(reminders)

    input("Hit any key to disconnect")

    await connection.disconnect()
    logger.debug("--- END OF TESTS ---")


def convert_time_string_to_epoch(time_string):
    try:
        # Create a datetime object with today's date and the provided time
        time_object = datetime.strptime(time_string, "%H:%M:%S")

        # Get the timestamp in seconds since the epoch
        timestamp = time_object.timestamp()

        return timestamp
    except ValueError:
        print("Invalid time format. Please use the format HH:MM:SS.")
        return None
