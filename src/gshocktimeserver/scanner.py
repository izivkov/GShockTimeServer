import logging
import sys

from bleak import BleakScanner
from configurator import conf


class Scanner:
    logger = logging.getLogger("scanner")
    CASIO_SERVICE_UUID = "00001804-0000-1000-8000-00805f9b34fb"

    async def scan(self):
        self.logger.info("starting scan...")

        scanner = BleakScanner()

        self.logger.warning("Scanning for devices...")

        device_address = conf.get("device.address")
        if device_address is None:
            filter = {"name": "CASIO*"}
            device = await scanner.find_device_by_filter(
                lambda d, ad: d.name and d.name.lower().startswith("casio")
            )
            if device is None:
                return

            conf.put("device.address", device.address)
            conf.put("device.name", device.name)
        else:
            self.logger.warning("Waiting for device by address...")
            device = await scanner.find_device_by_address(
                device_address, sys.float_info.max
            )

        return device
