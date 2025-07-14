# GShockTimeServer

## Announcement

This project is now split into two separate repositories:

- **GShockTimeServer**
- **gashock_api**

The **GShockTimeServer** repository contains the server-side code for setting the time on your G-Shock watch.

The **gashock_api** repository can be found [here](https://github.com/izivkov/gshock_api), and contains a Python API library for developing applications for these watches. Please refer to the **gashock_api** repository for the latest updates and documentation.

If you just like to include the API in your project, you can install it using pip:

```bash
pip install gashock-api
```

## Overview

GShockTimeServer allows you to set the correct time on your Casio G-Shock watches. Most G-Shock and other Casio Bluetooth watches are supported. Please give us feedback if your watch does not work.

## Usage

This app can run on any device with Python and Bluetooth capabilities—from a desktop to a Raspberry Pi Zero.  
It has been tested on Linux but should also work on Windows.

![Pi Zero Running the Server](images/pizero.jpg)

### Setting the Time

1. Ensure the app is running on your device.
2. Short-press the **lower-right** button on your G-Shock watch to connect.
3. Once connected, the app will automatically set the correct time on your watch.
4. If **AUTO TIME ADJUSTMENT** is enabled, the watch will sync up to **four times daily**.

## Dependencies

This project requires the following Python packages:

```
pytz
bleak
gashock-api
```

You can install them using the following command:

```bash
pip3 install -r requirements.txt
```

Then run:

```bash
python3 src/gshock_server.py [--multi-watch] [--fine-adjustment-secs secs]
```

The optional `--multi-watch` parameter allows you to connect if you have multiple watches.
The optional `--fine-adjustment-secs` alows you to fine adjust the time setting by providing an offset in seconds. For example:
```
python3 src/gshock_server.py --fine-adjustment-secs -9
```
will set the watches time 9 secods vefore the computer's time.

On pi zero get from github:

```
git clone https://github.com/izivkov/gshock-server-dist.git
```
## 🛠️ Hardware Requirements

---

### ✅ Supported Display Types

The system supports three display drivers. Choose the appropriate one for your hardware and pass it via the `--display` flag.

| Display Type | Description                                    | Notes                                      |
|--------------|------------------------------------------------|--------------------------------------------|
| `waveshare`  | Waveshare 1.54" e-paper or LCD module          | Widely available SPI displays. Requires driver and proper wiring. |
| `ftp154`     | 1.54" TFT LCD display (FTP154)                 | Full-color TFT screen, often used with ST7789 driver. |
| `mock`       | No physical display                            | Simulates a display in logs for testing purposes. Useful for headless/server environments. |

Example usage:

```bash
python gshock_server.py --multi-watch --display waveshare

If running as a service, the install script will prompt you to choose the display type.
💻 Host Computer or SBC

    Recommended: Raspberry Pi 3/4 or other Linux-capable SBC

    OS: Any modern Linux distribution

    Python: 3.8 or higher

    Dependencies are installed via the requirements.txt file

📶 Bluetooth

    Required: Bluetooth Low Energy (BLE) adapter

        Raspberry Pi 3/4 includes built-in BLE

        USB BLE dongles are supported on other devices

🔌 Power Supply

    5V power supply capable of powering both the SBC and the display

    Follow display datasheet specs for current and voltage tolerances

🧰 Optional Accessories

    HDMI screen, keyboard, and mouse for setup (not needed after initial install)

    Wi-Fi or Ethernet for network access

    USB-to-Serial debugger for troubleshooting (if needed)

📝 Notes

    Connect SPI/I²C displays according to their datasheets and match GPIO pins with your driver settings

    You can switch displays by editing the systemd service file or rerunning the installer

    The mock display is great for development, CI, and testing without any attached screen


## Troubleshooting
If your watch is not connecting, remove `config.ini` file and try again.

To see output from the service do:
```
journalctl -u gshock.service -f
```




