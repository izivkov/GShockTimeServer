import asyncio
import logging
import json
import pytz
import sys
from datetime import datetime, timezone

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from scanner import Scanner
from connection import Connection
from gshock_api import GshockAPI
from casio_watch import settings
from event import Event, create_event_date, RepeatPeriod, day_of_week
from casio_watch import WatchButton
from utils import (
    to_ascii_string,
    clean_str,
)
from configurator import conf

logger = logging.getLogger(__name__)
scanner = Scanner()


async def main(argv):
    await run_time_server(argv)
    # await run_api_tests()


async def run_time_server(argv):
    while True:
        try:
            if len(argv) > 0 and argv[0] == "--multy_watch":
                address = None
            else:
                address = conf.get("device.address")

            device = await scanner.scan(address)
            logger.info("Found: {}".format(device))

            connection = Connection(device)
            await connection.connect()

            api = GshockAPI(connection)

            pressed_button = await api.get_pressed_button()
            if (
                pressed_button != WatchButton.LOWER_RIGHT
                and pressed_button != WatchButton.NO_BUTTON
            ):
                continue

            await api.get_app_info()
            await api.set_time()

            await connection.disconnect()

        except Exception as e:
            print (f"Got error: {e}")
            continue


async def run_api_tests():
    device = await scanner.scan()
    logger.info("Found: {}".format(device))

    connection = Connection(device)
    await connection.connect()

    api = GshockAPI(connection)

    await api.get_app_info()

    pressed_button = await api.get_pressed_button()
    logger.info("pressed button: {}".format(pressed_button))

    watch_name = await api.get_watch_name()
    logger.info("got watch name: {}".format(watch_name))

    await api.set_time()
    # await api.reset_hand_to_12()

    alarms = await api.get_alarms()
    logger.info("alarms: {}".format(alarms))

    alarms[3]["enabled"] = True
    alarms[3]["hour"] = 7
    alarms[3]["minute"] = 25
    await api.set_alarms(alarms)

    seconds = await api.get_timer()
    logger.info("timer: {} seconds".format(seconds))

    await api.set_timer(seconds + 10)
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
    event = Event().create_event(json.loads(event_json_str))

    reminders = await api.get_reminders()
    for reminder in reminders:
        logger.info("reminder: {}".format(reminder.__str__()))

    await api.set_reminders(reminders)

    # input("Hit any key to disconnect")

    await connection.disconnect()
    logger.info("--- END OF TESTS ---")


if __name__ == "__main__":
    log_level = logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )
    asyncio.run(main(sys.argv[1:]))
