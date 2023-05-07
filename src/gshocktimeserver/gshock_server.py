import argparse
import asyncio
import logging
import json
import pytz
from datetime import datetime,timezone

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from scanner import Scanner
from connection import Connection
from gshock_api import GshockAPI
from casio_watch import settings
from event import Event, createEventDate, RepeatPeriod, DayOfWeek
from casio_watch import WATCH_BUTTON

logger = logging.getLogger(__name__)
scanner = Scanner()

async def main():
    # await run_time_server()
    await run_api_tests()

async def run_time_server():
    while True:
        try:
            device = await scanner.scan()
            logger.warning("Found: {}".format(device))

            connection = Connection(device)
            await connection.connect()

            api = GshockAPI(connection)

            pressed_button = await api.getPressedButton()
            if pressed_button != WATCH_BUTTON.LOWER_RIGHT and pressed_button != WATCH_BUTTON.NO_BUTTON:
                continue

            await api.get_app_info()
            await api.setTime()

            await connection.disconnect()

        except Exception as e:
            continue

async def run_api_tests():
    device = await scanner.scan()
    logger.warning("Found: {}".format(device))

    connection = Connection(device)
    await connection.connect()

    api = GshockAPI(connection)

    await api.get_app_info()

    pressed_button = await api.getPressedButton()
    logger.info("pressed button: {}".format(pressed_button))

    watch_name = await api.getWatchName()
    logger.error("got watch name: {}".format(watch_name))

    await api.setTime()

    alarms = await api.getAlarms()
    logger.info("alarms: {}".format(alarms))

    alarms[3]['enabled'] = True
    alarms[3]['hour'] = 7
    alarms[3]['minute'] = 25
    await api.setAlarms(alarms)

    seconds = await api.getTimer()
    logger.info("timer: {} seconds".format(seconds))

    await api.setTimer(seconds+10)
    time_adjstment = await api.get_time_adjustment()
    logger.info("time_adjstment: {}".format(time_adjstment))

    settings.timeAdjustment = True
    await api.set_time_adjustment(settings)

    settings_local = await api.get_basic_settings()
    logger.info("settings: {}".format(settings_local))

    settings_local["button_tone"] = True
    settings_local["language"] = "Engish"
    settings_local["time_format"] = "12h"

    await api.set_settings(settings_local)

    # Create a single event
    tz = pytz.timezone('America/Toronto') 
    dt = datetime.now(timezone.utc)
    utc_timestamp = dt.timestamp()
    event_date = createEventDate(utc_timestamp, tz) 
    event_date_str = json.dumps(event_date.__dict__)
    event_json_str = ("""{"title":"Test Event", "time":{"selected":\"""" + str(False) +  """\", "enabled":\"""" + str(True) + """\", "repeatPeriod":\""""+RepeatPeriod.WEEKLY+"""\","daysOfWeek":\"""" + "MONDAY" + """\", "startDate":"""+event_date_str+""", "endDate":"""+event_date_str+"""}}""")
    event = Event().createEvent(json.loads(event_json_str))

    reminders = await api.get_reminders()
    for reminder in reminders:
        logger.warning("reminder: {}".format(reminder.__str__()))

    await api.set_reminders(reminders)

    await connection.disconnect()
    logger.warning("--- END OF TESTS ---")


if __name__ == "__main__":
    asyncio.run(main())
