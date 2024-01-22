import calendar
import json
import pytz
import time
from datetime import datetime, timezone

from connection import Connection
from gshock_api import GshockAPI
from event import Event, create_event_date, RepeatPeriod
from scanner import scanner
from logger import logger


def prompt():
    logger.info(
        "========================================================================"
    )
    logger.info(
        "Press and hold lower-left button on your watch for 3 seconds to start..."
    )
    logger.info(
        "========================================================================"
    )
    logger.info("")


async def run_api_tests():
    prompt()

    device = await scanner.scan()
    logger.info("Found: {}".format(device))

    connection = Connection(device)
    await connection.connect()

    api = GshockAPI(connection)

    app_info = await api.get_app_info()
    logger.info("app info: {}".format(app_info))

    pressed_button = await api.get_pressed_button()
    logger.info("pressed button: {}".format(pressed_button))

    watch_name = await api.get_watch_name()
    logger.info("got watch name: {}".format(watch_name))

    await api.set_time()

    alarms = await api.get_alarms()
    logger.info("alarms: {}".format(alarms))

    alarms[3]["enabled"] = True
    alarms[3]["hour"] = 7
    alarms[3]["minute"] = 25
    alarms[3]["enabled"] = False
    await api.set_alarms(alarms)

    seconds = await api.get_timer()
    logger.info("timer: {} seconds".format(seconds))

    await api.set_timer(seconds + 10)
    time_adjstment = await api.get_time_adjustment()
    logger.info("time_adjstment: {}".format(time_adjstment))

    await api.set_time_adjustment(time_adjustement=True, minutes_after_hour=10)

    condition = await api.get_watch_condition()
    logger.info(f"condition: {condition}")

    settings_local = await api.get_basic_settings()
    logger.info("settings: {}".format(settings_local))

    settings_local["button_tone"] = True
    settings_local["language"] = "Russian"
    settings_local["time_format"] = "24h"

    await api.set_settings(settings_local)

    settings_local = await api.get_basic_settings()
    logger.info("After update: settings: {}".format(settings_local))

    # Create a single event
    tz = pytz.timezone("America/Toronto")
    dt = datetime.now(timezone.utc)
    utc_timestamp = dt.timestamp()
    event_date = create_event_date(utc_timestamp, tz)
    event_date_str = json.dumps(event_date.__dict__)
    event_json_str = (
        """{"title":"Test Event", "time":{"selected":\""""
        + str(False)
        + """\", "enabled":\""""
        + str(True)
        + """\", "repeat_period":\""""
        + RepeatPeriod.WEEKLY
        + """\","days_of_week":\""""
        + "MONDAY"
        + """\", "start_date":"""
        + event_date_str
        + """, "end_date":"""
        + event_date_str
        + """}}"""
    )
    Event().create_event(json.loads(event_json_str))
    logger.info("Created event: {}".format(event_json_str))

    reminders = await api.get_reminders()
    for reminder in reminders:
        logger.info("reminder: {}".format(reminder.__str__()))

    reminders[3]["title"] = "Test Event"

    await api.set_reminders(reminders)

    input("Hit any key to disconnect")

    await connection.disconnect()
    logger.info("--- END OF TESTS ---")


def convert_time_string_to_epoch(time_string):
    try:
        # Create a datetime object with today's date and the provided time
        time_object = datetime.strptime(time_string, "%H:%M:%S")

        # Get the timestamp in seconds since the epoch
        timestamp = time_object.timestamp()

        return timestamp
    except ValueError:
        logger.info("Invalid time format. Please use the format HH:MM:SS.")
        return None
