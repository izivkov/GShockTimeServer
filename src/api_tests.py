import asyncio
import sys

import json
import time
import pytz
from datetime import datetime, timezone

import sys
print(sys.executable)

from gshock_api.connection import Connection
from gshock_api.gshock_api import GshockAPI
from gshock_api.event import Event, create_event_date, RepeatPeriod
from gshock_api.scanner import scanner
from gshock_api.logger import logger
from gshock_api.app_notification import AppNotification, NotificationType
from gshock_api.configurator import conf

async def main(argv):
    await run_api_tests(argv)
    await run_api_tests_notifications()

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

    address = conf.get("device.address")
    
    connection = Connection(address)
    await connection.connect()

    api = GshockAPI(connection)

    app_info = await api.get_app_info()
    logger.info("app info: {}".format(app_info))

    pressed_button = await api.get_pressed_button()
    logger.info("pressed button: {}".format(pressed_button))

    watch_name = await api.get_watch_name()
    logger.info("got watch name: {}".format(watch_name))

    await api.set_time(time.time()+10*60)

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

    await app_notifications(api)
    logger.info("After app_notifications")

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
        + str(RepeatPeriod.WEEKLY)
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

async def run_api_tests_notifications():
    prompt()

    connection = Connection()
    await connection.connect()

    api = GshockAPI(connection)

    await app_notifications(api)

    input("Hit any key to disconnect")

    await connection.disconnect()
    logger.info("--- END OF TESTS ---")

async def app_notifications(api):

    calendar_notification = AppNotification(
        type = NotificationType.CALENDAR,
        timestamp="20231001T121000",
        app = "Calendar",
        title = "This is a very long Meeting with Team",
        text =" 9:20 - 10:15 AM"
    )

    calendar_notification_all_day = AppNotification(
        type = NotificationType.CALENDAR,
        timestamp="20250516T233000",
        app = "Calendar",
        title = "Full day event 3",
        text = "Tomorrow",
    )

    email_notification2 = AppNotification(
        type = NotificationType.EMAIL_SMS,
        timestamp="20250516T211520",
        app="Gmail",
        title="me",
        text="""\u5f7c\u5973\u306f\u30d4\u30a2\n\u5f7c\u5973\u306f\u30d4\u30a2\u30ce\u3092\u5f3e\u3044\u305f\u308a\u3001\u7d75\u3092\u63cf\u304f\u306e\u304c\u597d\u304d\u3067\u3059\u3002\u30ea\u30a2\u5145\u3067\u3059\n
        \u5f7c\u5973\u306f\u30d4\u30a2\n\u5f7c\u5973\u306f\u30d4\u30a2\u30ce\u3092\u5f3e\u3044\u305f\u308a\u3001\u7d75\u3092\u63cf\u304f\u306e\u304c\u597d\u304d\u3067\u3059\u3002\u30ea\u30a2\u5145\u3067\u3059\n
        \u5f7c\u5973\u306f\u30d4\u30a2\n\u5f7c\u5973\u306f\u30d4\u30a2\u30ce\u3092\u5f3e\u3044\u305f\u308a\u3001\u7d75\u3092\u63cf\u304f\u306e\u304c\u597d\u304d\u3067\u3059\u3002\u30ea\u30a2\u5145\u3067\u3059\n
        """,
        short_text = """\u5f7c\u5973\u306f\u30d4\u30a2\n\u5f7c\u5973\u306f\u30d4\u30a2\u30ce\u3092\u5f3e\u3044\u305f\u308a\u3001\u7d75\u3092\u63cf\u304f\u306e\u304c\u597d\u304d\u3067\u3059\u3002\u30ea\u30a2\u5145\u3067\u3059\n
        \u5f7c\u5973\u306f\u30d4\u30a2\n\u5f7c\u5973\u306f\u30d4\u30a2\u30ce\u3092\u5f3e\u3044\u305f\u308a\u3001\u7d75\u3092\u63cf\u304f\u306e\u304c\u597d\u304d\u3067\u3059\u3002\u30ea\u30a2\u5145\u3067\u3059\n
        \u5f7c\u5973\u306f\u30d4\u30a2\n\u5f7c\u5973\u306f\u30d4\u30a2\u30ce\u3092\u5f3e\u3044\u305f\u308a\u3001\u7d75\u3092\u63cf\u304f\u306e\u304c\u597d\u304d\u3067\u3059\u3002\u30ea\u30a2\u5145\u3067\u3059\n
        """
    )

    email_notificationArabic = AppNotification(
        type = NotificationType.EMAIL_SMS,
        timestamp="20250516T211520",
        app="Gmail",
        title="me",
        text="الساعة\n"
    )

    email_notification = AppNotification(
        type = NotificationType.EMAIL,
        timestamp="20231001T120000",
        app="EmailApp",
        title="Ivo",
        short_text = """And this is a short message up to 40 chars""",
        text="This is the message up to 193 characters, combined up to 206 characters",
    )

    await api.send_app_notification(email_notification2)

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


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))