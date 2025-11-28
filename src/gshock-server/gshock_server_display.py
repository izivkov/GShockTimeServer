import asyncio
import sys
import time
from datetime import datetime, timedelta
from typing import List, Tuple

from gshock_api.connection import Connection
from gshock_api.gshock_api import GshockAPI
from gshock_api.iolib.button_pressed_io import WatchButton
from gshock_api.logger import logger
from args import args
from gshock_api.watch_info import watch_info
from utils import run_once_key
from persistent_store import PersistentMap
from gshock_api.always_connected_watch_filter import always_connected_watch_filter as watch_filter


__author__ = "Ivo Zivkov"
__copyright__ = "Ivo Zivkov"
__license__ = "MIT"


async def main(argv: List[str]) -> None:
    await run_time_server()


store = PersistentMap("gshock_server_data.json")


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


def get_display(display_type: str) -> object:
    if display_type == "mock":
        from display.mock_display import MockDisplay
        return MockDisplay()
    elif display_type == "waveshare":
        from display.waveshare_display import WaveshareDisplay
        return WaveshareDisplay()
    elif display_type == "tft154":
        from display.tft154_display import TFT154Display
        return TFT154Display()
    else:
        raise ValueError(f"Unsupported display type: {display_type}")


oled = get_display(args.display)


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
            alarm_time_tomorrow = alarm_time_today + timedelta(days=1)
            times_tomorrow.append(alarm_time_tomorrow)

    if times_today:
        next_alarm = min(times_today)
    elif times_tomorrow:
        next_alarm = min(times_tomorrow)
    else:
        return None

    return next_alarm.hour, next_alarm.minute


async def show_display(api: GshockAPI) -> None:
    try:
        alarms = await api.get_alarms()
        hour, minute = get_next_alarm_time(alarms)
        if hour is not None and minute is not None:
            alarm_str = f"{hour:02d}:{minute:02d}"
        else:
            alarm_str = "Invalid time"

        reminders = await api.get_reminders()
        reminder_title = reminders[0].get("title") if reminders else "None"
        condition = await api.get_watch_condition()
        battery = condition.get("battery_level_percent")
        temperature = condition.get("temperature")
        name = watch_info.name
        short_name = ' '.join(name.strip().split()[1:])

        oled.show_status(
            watch_name=short_name,
            battery=battery,
            temperature=temperature,
            last_sync=datetime.now().strftime("%m/%d %H:%M"),
            alarm=alarm_str,
            reminder=reminder_title,
            auto_sync="On" if await api.get_time_adjustment() else "Off",
        )
    except Exception as e:
        logger.error(f"Got error: {e}")


async def safe_set_time(api: GshockAPI, offset: int = 0) -> None:
    try:
        await api.set_time(offset=offset)
    except Exception as e:
        logger.error(f"Got error while setting time: {e}")


async def safe_show_display(api: GshockAPI) -> None:
    try:
        await show_display(api)
    except Exception as e:
        logger.error(f"Got error while showing display: {e}")


async def run_time_server() -> None:
    pressed_button: WatchButton = WatchButton.NO_BUTTON

    prompt()

    while True:
        connection: Connection | None = None

        await asyncio.sleep(1)

        try:
            run_once_key(
                "show_welcome_screen",
                oled.show_welcome_screen,
                "Waiting\nfor connection...",
                watch_name=store.get("watch_name", None),
                last_sync=store.get("last_connected", None),
            )

            logger.info("Waiting for Connection...")

            connection = Connection(address=None)
            connected = await connection.connect(watch_filter.connection_filter)
            if not connected:
                logger.info("Failed to connect")
                continue

            oled.show_welcome_screen(message="Connected!")

            store.add("last_connected", datetime.now().strftime("%m/%d %H:%M"))
            store.add("watch_name", watch_info.name)

            api = GshockAPI(connection)
            pressed_button = await api.get_pressed_button()

            if pressed_button not in [WatchButton.LOWER_RIGHT, WatchButton.NO_BUTTON, WatchButton.LOWER_LEFT]:
                continue

            fine_adjustment_secs = args.fine_adjustment_secs
            await safe_set_time(api, offset=int(fine_adjustment_secs))

            logger.info(f"Time set at {datetime.now()} on {watch_info.name}")

            if pressed_button == WatchButton.LOWER_LEFT:
                await safe_show_display(api)
            elif pressed_button in [WatchButton.LOWER_RIGHT, WatchButton.NO_BUTTON]:
                oled.show_welcome_screen(
                    "Waiting\nfor connection...",
                    watch_name=store.get("watch_name", None),
                    last_sync=store.get("last_connected", None),
                )

            if not watch_info.alwaysConnected:
                try:
                    await connection.disconnect()
                except Exception as e:
                    logger.error(f"Got error while disconnecting: {e}")

        except Exception as e:
            logger.error(f"Got error: {e}")

            oled.show_welcome_screen(
                "Waiting\nfor connection...",
                watch_name=store.get("watch_name", None),
                last_sync=store.get("last_connected", None),
            )
        finally:
            pass


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
