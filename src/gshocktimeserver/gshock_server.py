import asyncio
import sys

from datetime import datetime

from connection import Connection
from gshock_api import GshockAPI
from iolib.button_pressed_io import WatchButton
from scanner import scanner
from configurator import conf
from logger import logger
from args import args
from api_tests import run_api_tests
from watch_info import watch_info

__author__ = "Ivo Zivkov"
__copyright__ = "Ivo Zivkov"
__license__ = "MIT"


async def main(argv):
    await run_time_server()
    # await run_api_tests()


def prompt():
    logger.info(
        "=============================================================================================="
    )
    logger.info("Short-press lower-right button on your watch to set time...")
    logger.info("")
    logger.info(
        "If Auto-time set on watch, the watch will connect and run automatically up to 4 times per day."
    )
    logger.info(
        "=============================================================================================="
    )
    logger.info("")


async def run_time_server():
    prompt()

    while True:
        try:
            if args.get().multi_watch:
                address = None
            else:
                address = conf.get("device.address")

            device = await scanner.scan(address)
            logger.debug("Found: {}".format(device))

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
            logger.info(f"Time set at {datetime.now()} on {watch_info.name}")

            # You can add mail notification here if you run your mail server.
            # send_mail_notification(args.mailto)

            await connection.disconnect()

        except Exception as e:
            logger.error(f"Got error: {e}")
            continue


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
