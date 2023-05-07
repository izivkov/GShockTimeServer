import logging

from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from casio_constants import CasioConstants
from utils import to_casio_cmd
from data_watcher import data_watcher
from casio_watch import to_json, callWriter


class Connection:
    logger = logging.getLogger("connection")

    def __init__(self, device):
        self.handles_map = self.initHandlesMap()
        self.device = device
        self.client = BleakClient(device)

    def notification_handler(
        self, characteristic: BleakGATTCharacteristic, data: bytearray
    ):
        """Simple notification handler which prints the data received."""
        json = to_json(data)
        name = list(dict(json).keys())[0]
        value = list(dict(json).values())[0]
        data_watcher.emit_event(name, value)

    async def connect(self):
        try:
            await self.client.connect()
            await self.client.start_notify(
                CasioConstants.CASIO_ALL_FEATURES_CHARACTERISTIC_UUID,
                self.notification_handler,
            )
            return True
        except Exception as e:
            self.logger.warning(f"Cannot connect: {e}")
            return False

    async def disconnect(self):
        await self.client.disconnect()

    async def write(self, handle, data):
        self.logger.info("write: {}".format(data))
        try:
            await self.client.write_gatt_char(
                self.handles_map[handle], to_casio_cmd(data)
            )
        except Exception as e:
            self.logger.info("write failed with exception: {}".format(e))

    async def request(self, request):
        await self.write(0xC, request)

    def initHandlesMap(self):
        handles_map = {}

        handles_map[0x04] = CasioConstants.CASIO_GET_DEVICE_NAME
        handles_map[0x06] = CasioConstants.CASIO_APPEARANCE
        handles_map[0x09] = CasioConstants.TX_POWER_LEVEL_CHARACTERISTIC_UUID
        handles_map[
            0x0C
        ] = CasioConstants.CASIO_READ_REQUEST_FOR_ALL_FEATURES_CHARACTERISTIC_UUID
        handles_map[0x0E] = CasioConstants.CASIO_ALL_FEATURES_CHARACTERISTIC_UUID
        handles_map[0x11] = CasioConstants.CASIO_DATA_REQUEST_SP_CHARACTERISTIC_UUID
        handles_map[0x14] = CasioConstants.CASIO_CONVOY_CHARACTERISTIC_UUID
        handles_map[0xFF] = CasioConstants.SERIAL_NUMBER_STRING

        return handles_map

    async def sendMessage(self, message):
        await callWriter(self, message)
