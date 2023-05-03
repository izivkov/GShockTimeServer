import logging

from bleak import BleakScanner

class Scanner:

    logger = logging.getLogger("scanner")
    CASIO_SERVICE_UUID = '00001804-0000-1000-8000-00805f9b34fb'

    async def scan(self):
        self.logger.info("starting scan...")
        scanner = BleakScanner()

        while True:
            self.logger.info("Scanning for devices...")
            # devices = await scanner.discover(timeout=5.0, return_adv=True, cb=dict(use_bdaddr=False))
            
            filter = {
                "name": "CASIO*",
            }
            device = await scanner.find_device_by_filter(
                # lambda d, ad: self.CASIO_SERVICE_UUID in d.details["props"]["UUIDs"])
                lambda d, ad: d.name and d.name.lower().startswith("casio"))
            if (device == None):
                continue

            return device



    