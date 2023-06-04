import argparse
import asyncio
import logging
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

__author__ = "Ivo Zivkov"
__copyright__ = "Ivo Zivkov"
__license__ = "MIT"

logger = logging.getLogger(__name__)

async def main(argv):
    args = parse_args(argv)
    await run_time_server(args)
    # await run_api_tests(args)


async def run_time_server(args):
    while True:
        try:
            if args.multi_watch == True:
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

            # You can add mail notification here if you run your mail server
            # send_mail_notification(args.mailto)

            await connection.disconnect()

        except Exception as e:
            print (f"Got error: {e}")
            continue

def parse_args(args):
    parser = argparse.ArgumentParser(description="Parser")
    parser.add_argument(
        "--multi-watch", action='store_true', help="--multi-watch allows use of multimple watches"
    )
    parser.add_argument(
        "--mailto", help="email when time set to email address", required=False
    )
    return parser.parse_args(args)

if __name__ == "__main__":
    log_level = logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )
    asyncio.run(main(sys.argv[1:]))

