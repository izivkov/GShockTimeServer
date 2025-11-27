import asyncio
import sys
import time
from datetime import datetime, timedelta
from typing import List, Tuple

from gshock_api.connection import Connection
from gshock_api.gshock_api import GshockAPI
from gshock_api.iolib.button_pressed_io import WatchButton
from gshock_api.logger import logger
from gshock_api.watch_info import watch_info
from args import args
from peristent_store import PersistentMap
from gshock_api.always_connected_watch_filter import always_connected_watch_filter as watch_filter


__author__ = "Ivo Zivkov"
__copyright__ = "Ivo Zivkov"
__license__ = "MIT"


async def main(argv: List[str]) -> None:
    await run_time_server()


def prompt() -> None:
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


def get_next_alarm_time(alarms: List[dict[str, int]]) -> Tuple[int, int] | None:
    now = datetime.now()
    today = now.date()
    times_today: List[datetime] = []
    times_tomorrow: List[datetime] = []

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
        return None

    return next_alarm.hour, next_alarm.minute


async def run_time_server() -> None:
    store = PersistentMap("gshock_server_data.json")
    prompt()

    while True:
        try:
            # avoud tight loops
            time.sleep(1)

            logger.info("Waiting for Connection...")

            connection = Connection()
            connected = await connection.connect(
                lambda name: name not in ["CASIO OCW-T200"] and watch_filter.connection_filter(name)
            )

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

            await api.set_time(offset=int(fine_adjustment_secs))

            logger.info(f"Time set at {datetime.now()} on {watch_info.name}")

            if not watch_info.alwaysConnected:
                await connection.disconnect()

        except Exception as e:
            logger.error(f"Got error: {e}")
            continue


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
