from bleak import BleakClient
from bleak.backends.characteristic import BleakGATTCharacteristic
from casio_constants import CasioConstants
import message_dispatcher
from utils import to_casio_cmd
from logger import logger


class Connection:
    def __init__(self, device):
        self.handles_map = self.init_handles_map()
        self.device = device
        self.client = BleakClient(device)

    def notification_handler(
        self, characteristic: BleakGATTCharacteristic, data: bytearray
    ):
        message_dispatcher.MessageDispatcher.on_received(data)

    async def connect(self):
        try:
            await self.client.connect()
            await self.client.start_notify(
                CasioConstants.CASIO_ALL_FEATURES_CHARACTERISTIC_UUID,
                self.notification_handler,
            )
            return True
        except Exception as e:
            logger.debug(f"Cannot connect: {e}")
            return False

    async def disconnect(self):
        await self.client.disconnect()

    async def write(self, handle, data):
        try:
            await self.client.write_gatt_char(
                self.handles_map[handle], to_casio_cmd(data)
            )
        except Exception as e:
            logger.debug("write failed with exception: {}".format(e))

    async def request(self, request):
        logger.info("write: {}".format(request))
        await self.write(0xC, request)

    def init_handles_map(self):
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
        # await callWriter(self, message)
        await message_dispatcher.MessageDispatcher.send_to_watch(message)
