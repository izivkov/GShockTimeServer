import asyncio
import sys

from datetime import datetime
import time

from gshock_api.connection import Connection
from gshock_api.gshock_api import GshockAPI
from gshock_api.iolib.button_pressed_io import WatchButton
from gshock_api.scanner import scanner
from gshock_api.logger import logger
from gshock_api.watch_info import watch_info
from gshock_api.watch_info import watch_info
from args import args
from datetime import datetime, timedelta
from configurator import conf

__author__ = "Ivo Zivkov"
__copyright__ = "Ivo Zivkov"
__license__ = "MIT"

async def main(argv):
    await run_time_server()

def prompt():
    logger.info(
        "=============================================================================================="
    )
    logger.info("Long-press LOWER-LEFT button on your watch to set time...")
    logger.info("")
    logger.info(
        "If Auto-time set on watch, the watch will connect and run automatically up to 4 times per day."
    )
    logger.info(
        "=============================================================================================="
    )
    logger.info("")

def get_next_alarm_time(alarms):
    now = datetime.now()
    today = now.date()
    times_today = []
    times_tomorrow = []

    for alarm in alarms:
        if not alarm.get("enabled", True):
            continue
        hour = alarm.get("hour")
        minute = alarm.get("minute")
        if not (isinstance(hour, int) and isinstance(minute, int)):
            continue
        alarm_time_today = datetime.combine(today, datetime.min.time()).replace(hour=hour, minute=minute)
        if alarm_time_today > now:
            times_today.append(alarm_time_today)
        else:
            # For tomorrow
            alarm_time_tomorrow = alarm_time_today + timedelta(days=1)
            times_tomorrow.append(alarm_time_tomorrow)

    if times_today:
        next_alarm = min(times_today)
    elif times_tomorrow:
        next_alarm = min(times_tomorrow)
    else:
        return None, None

    return next_alarm.hour, next_alarm.minute

from peristent_store import PersistentMap

async def run_time_server():
    excluded_watches = conf.get("excluded_watches")
    store = PersistentMap("gshock_server_data.json")
    prompt()

    while True:
        try:
            
            logger.info(f"Waiting for Connection...")

            connection = Connection()
            connected = await connection.connect(excluded_watches)
            if not connected:
                logger.info("Failed to connect")
                continue

            logger.info(f"Connected to {watch_info.name} ({watch_info.address})")
            store.add("last_connected", datetime.now().strftime("%m/%d %H:%M"))
            store.add("watch_name", watch_info.name)
 
            api = GshockAPI(connection)
            pressed_button = await api.get_pressed_button()
            if (
                pressed_button != WatchButton.LOWER_RIGHT
                and pressed_button != WatchButton.NO_BUTTON
                and pressed_button != WatchButton.LOWER_LEFT
            ):
                continue

            # Apply fine adjustment to the time
            fine_adjustment_secs = args.fine_adjustment_secs
            
            await api.set_time(offset = int(fine_adjustment_secs))

            logger.info(f"Time set at {datetime.now()} on {watch_info.name}")

            if watch_info.alwaysConnected == False:
                await connection.disconnect()

        except Exception as e:
            logger.error(f"Got error: {e}")
            continue

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
