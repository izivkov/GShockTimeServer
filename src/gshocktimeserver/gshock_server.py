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

logger = logging.getLogger(__name__)

async def main(args: argparse.Namespace):
    scanner = Scanner()
    device = await scanner.scan()
    logger.info("Found: {}".format(device))

    connection = Connection(device)
    await connection.connect()

    api = GshockAPI(connection)

    await api.get_app_info()

    # pressed_button = await api.getPressedButton()
    # logger.info("pressed button: {}".format(pressed_button))

    # watch_name = await api.getWatchName()
    # logger.info("got watch name: {}".format(watch_name))

    # await api.setTime()
    # alarms = await api.getAlarms()
    # logger.info("alarms: {}".format(alarms))

    # alarms[3]['enabled'] = True
    # alarms[3]['hour'] = 7
    # alarms[3]['minute'] = 25
    # await api.setAlarms(alarms)

    # seconds = await api.getTimer()
    # logger.info("timer: {} seconds".format(seconds))

    # await api.setTimer(seconds+10)
    # time_adjstment = await api.get_time_adjustment()
    # logger.info("time_adjstment: {}".format(time_adjstment))

    # settings.timeAdjustment = False
    # await api.set_time_adjustment(settings)

    # settings_local = await api.get_basic_settings()
    # logger.info("settings: {}".format(settings_local))

    # settings_local["button_tone"] = True
    # settings_local["language"] = "Engish"
    # settings_local["time_format"] = "12h"

    # await api.set_settings(settings_local)

    # tz = pytz.timezone('America/Toronto') 
    # dt = datetime.now(timezone.utc)
    # utc_timestamp = dt.timestamp()
    # event_date = createEventDate(utc_timestamp, tz) 
    # event_date_str = json.dumps(event_date.__dict__)
    # event_json_str = ("""{"time":"10002", "title":"Test Event", "selected":\"""" + str(False) +  """\", "enabled":\"""" + str(True) + """\", "repeatPeriod":\""""+RepeatPeriod.WEEKLY+"""\","daysOfWeek":\"""" + "MONDAY" + """\", "startDate":"""+event_date_str+""", "endDate":"""+event_date_str+"""}""")
    # event = Event(json.loads(event_json_str))

    reminders = await api.get_reminders()
    for reminder in reminders:
        logger.info("reminder: {}".format(reminder.__str__()))

    # await api.set_remonders(reminders)

    logger.info("--- END OF PROGRAM ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    device_group = parser.add_mutually_exclusive_group(required=True)

    device_group.add_argument(
        "--name",
        metavar="<name>",
        help="the name of the bluetooth device to connect to",
    )
    device_group.add_argument(
        "--address",
        metavar="<address>",
        help="the address of the bluetooth device to connect to",
    )

    parser.add_argument(
        "--macos-use-bdaddr",
        action="store_true",
        help="when true use Bluetooth address instead of UUID on macOS",
    )

    parser.add_argument(
        "characteristic",
        metavar="<notify uuid>",
        help="UUID of a characteristic that supports notifications",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="sets the log level to debug",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main(args))
