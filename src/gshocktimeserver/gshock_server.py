import asyncio
import sys

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
from scanner import scanner
from utils import (
    to_ascii_string,
    clean_str,
)
from configurator import conf
from api_tests import run_api_tests
from mailsener import send_mail_notification
from logger import logger
from args import args

__author__ = "Ivo Zivkov"
__copyright__ = "Ivo Zivkov"
__license__ = "MIT"

async def main(argv):
    await run_time_server()
    # await run_api_tests(args)


async def run_time_server():
    while True:
        try:
            if args.get().multi_watch == True:
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

            # You can add mail notification here if you run your mail server.
            # send_mail_notification(args.mailto)

            await connection.disconnect()

        except Exception as e:
            logger.error (f"Got error: {e}")
            continue

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))

