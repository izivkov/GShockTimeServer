import asyncio, time
from tracemalloc import start
from bleak import BleakClient
from bleak.exc import BleakDBusError
from bleak.backends.characteristic import BleakGATTCharacteristic
from gshock_api.casio_constants import CasioConstants
from gshock_api import message_dispatcher
from gshock_api.utils import to_casio_cmd
from gshock_api.logger import logger
from gshock_api.watch_info import watch_info
from bleak.backends.device import BLEDevice
from gshock_api.scanner import scanner
from gshock_api.exceptions import GShockIgnorableException, GShockConnectionError

class Connection:
    def __init__(self, address = None):
        self.handles_map = self.init_handles_map()
        self.address = address
        self.client: BleakClient = None
        self.characteristics_map = {}

    def notification_handler(
        self, characteristic: BleakGATTCharacteristic, data: bytearray
    ):
        message_dispatcher.MessageDispatcher.on_received(data)

    async def init_characteristics_map(self):
        """
        Prints all services and characteristics of the connected BLE device.
        """
        services = self.client.services
        for service in services:
            for char in service.characteristics:
                self.characteristics_map[char.uuid] = char.uuid  # Store in map

    async def connect(self, excluded_watches: list[str] | None = None) -> bool:
        try:
            # Scan for device if address not provided
            if self.address == None:
                device = await scanner.scan(
                    device_address=self.address if self.address else None,
                    excluded_watches=excluded_watches
                )
                if device is None:
                    logger.info("No G-Shock device found or name matches excluded watches.")
                    return False

                self.address = device.address  # Always update with actual device found

            self.client = BleakClient(self.address)
            await self.client.connect()
            if not self.client.is_connected:
                logger.info(f"Failed to connect to {self.address}")
                return False

            await self.init_characteristics_map()

            await self.client.start_notify(
                CasioConstants.CASIO_ALL_FEATURES_CHARACTERISTIC_UUID,
                self.notification_handler,
            )

            return True

        except Exception as e:
            logger.info(f"[GShock Connect] Connection failed: {e}")
            return False
        
    async def disconnect(self):
        await self.client.disconnect()

    def is_service_supported(self, handle):
        uuid = self.handles_map.get(handle)
        supported = (uuid not in self.characteristics_map)
        return supported

    async def write(self, handle, data):
        try:
            uuid = self.handles_map.get(handle)

            if (uuid not in self.characteristics_map):
                logger.info(
                    "write failed: handle {} not in characteristics map".format(handle)
                )
                if (handle == 13):
                    logger.info(
                        "Your watch does not support notifications..."
                    )
                return

            await self.client.write_gatt_char(
                uuid, to_casio_cmd(data)
            )

        except Exception as e:
            e.args = (type(e).__name__,)
            if isinstance(e, (BleakDBusError, EOFError)):
                raise GShockIgnorableException(e)
            else:
                raise GShockConnectionError(f"Unable to send time to watch: {e}") 

    async def request(self, request):
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
        handles_map[0x0D] = CasioConstants.CASIO_NOTIFICATION_CHARACTERISTIC_UUID
        handles_map[0x11] = CasioConstants.CASIO_DATA_REQUEST_SP_CHARACTERISTIC_UUID
        handles_map[0x14] = CasioConstants.CASIO_CONVOY_CHARACTERISTIC_UUID
        handles_map[0xFF] = CasioConstants.SERIAL_NUMBER_STRING

        return handles_map

    async def sendMessage(self, message):
        await message_dispatcher.MessageDispatcher.send_to_watch(message)
