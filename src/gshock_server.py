import asyncio
import sys

from datetime import datetime
import time

from gshock_api.connection import Connection
from gshock_api.gshock_api import GshockAPI
from gshock_api.iolib.button_pressed_io import WatchButton
from gshock_api.scanner import scanner
from gshock_api.configurator import conf
from gshock_api.logger import logger
from gshock_api.watch_info import watch_info
from args import args

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


async def show_display(api: GshockAPI):
    from display.oled_simulator import MockOLEDDisplay

    oled = MockOLEDDisplay()

    try:
        alarms = await api.get_alarms()
        hour = alarms[0].get("hour")
        minute = alarms[0].get("minute")
        if isinstance(hour, int) and isinstance(minute, int):
            alarm_str = f"{hour:02d}:{minute:02d}"
        else:
            alarm_str = "Invalid time"


        reminders = await api.get_reminders()
        reminder_title = reminders[0].get("title") or "No reminders"
        condition = await api.get_watch_condition()
        battery = condition.get("battery_level_percent")
        temperature = condition.get("temperature")
        name = await api.get_watch_name()
        short_name = ' '.join(name.strip().split()[1:])

        oled.show_status(
            watch_name=short_name,
            battery = battery,
            temperature = temperature,
            last_sync=datetime.now().strftime("%H:%M"),
            alarm= alarm_str,
            reminder=reminder_title,
            auto_sync="On" if await api.get_time_adjustment() else "Off",
        )
        print("🖼 OLED preview saved as 'oled_preview.png'")

    except Exception as e:
        logger.error(f"Got error: {e}")

async def run_time_server():
    prompt()

    while True:
        try:
            if args.get().multi_watch:
                address = None
            else:
                address = conf.get("device.address")

            logger.info(f"Before Connecting to watch at {address}...")
            connection = Connection(address)
            await connection.connect()
            logger.info(f"Connected to watch at {address}...")

            api = GshockAPI(connection)
            pressed_button = await api.get_pressed_button()
            if (
                pressed_button != WatchButton.LOWER_RIGHT
                and pressed_button != WatchButton.NO_BUTTON
                and pressed_button != WatchButton.LOWER_LEFT
            ):
                continue

            # Apply fine adjustment to the time
            fine_adjustment_secs = args.get().fine_adjustment_secs
            logger.info(f"Fine adjustment: {fine_adjustment_secs} seconds")  

            await api.set_time(int(time.time()) + fine_adjustment_secs)
            
            logger.info(f"Time set at {datetime.now()} on {watch_info.name}")

            # Only update the display of we have pressed LOWER-LEFT button,
            # Otherwise the watch will dicoinnect before we get all the information for the display.
            if pressed_button == WatchButton.LOWER_LEFT:
                await show_display(api)

            if watch_info.alwaysConnected == False:
                await connection.disconnect()

        except Exception as e:
            logger.error(f"Got error: {e}")
            continue


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
