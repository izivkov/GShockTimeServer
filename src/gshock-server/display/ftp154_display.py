from luma.core.interface.serial import spi
from luma.lcd.device import st7789
from display.display import Display
from PIL import Image, ImageDraw
    
class FTP154Display(Display):
    """
    """
    def __init__(self, width=240, height=240, i2c_port=1, i2c_address=0x3C):
        self.width = width
        self.height = height
        serial = spi(port=0, device=0, gpio_DC=24, gpio_RST=25)
        self.device = st7789(serial, width=240, height=240, rotate=0)
        
        self.image = Image.new("RGB", (self.width, self.height), color=0)
        self.draw = ImageDraw.Draw(self.image)

    def show_status(self, watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync):
        super().show_status(watch_name, battery, temperature, last_sync, alarm, reminder, auto_sync)

        self.device.display(self.image)


