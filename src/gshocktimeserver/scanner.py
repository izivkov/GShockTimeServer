import logging

from bleak import BleakScanner
from configurator import conf

class Scanner:

    logger = logging.getLogger("scanner")
    CASIO_SERVICE_UUID = '00001804-0000-1000-8000-00805f9b34fb'

    async def scan(self):
        self.logger.info("starting scan...")
        scanner = BleakScanner()

        while True:
            self.logger.info("Scanning for devices...")
            
            device_address = conf.get("device.address")
            if device_address == None:
                filter = {"name": "CASIO*"}
                device = await scanner.find_device_by_filter(lambda d, ad: d.name and d.name.lower().startswith("casio"))
                if (device == None):
                    continue

                conf.put("device.address", device.address)
                conf.put("device.name", device.name)
            else:
                device = await scanner.find_device_by_address(device_address)

            return device



    