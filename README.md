# GShockTimeServer

## Overview

GShockTimeServer allows you to set the correct time on your Casio G-Shock watches. Most G-Shock and other Casio Bluetooth watches are supported. Please give us feedback if your watch does not work.

## Usage

This app can run on any device with Python and Bluetooth capabilities—from a desktop to a Raspberry Pi Zero.  
It has been tested on Linux but should also work on Windows.


### Setting the Time

1. Ensure the app is running on your device.
2. Short-press the **lower-right** button on your G-Shock watch to connect.
3. Once connected, the app will automatically set the correct time on your watch.
4. If **AUTO TIME ADJUSTMENT** is enabled, the watch will sync up to **four times daily**.

## Manual Minimal Setup

If you like to run the timer server on any Linux or Windows PC, here os how to do it. First you need to install
the follwoing dependencies:

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

## Hardware
You can run the server on a Pi 3/4 or Pi Zero device, optionally with LCD displays. Currently we support 
the following 240x240 color displays:

| Display Type | Description                                    | Notes                                      |
|--------------|------------------------------------------------|--------------------------------------------|
| `waveshare`  | Waveshare 1.3" SPI LCD module HAT, ST7789 Controller  | Widely available LCD color display. Directly plugs into the 40-pin header of the Pi |
| `ftp154`     | 1.54"-TFT-SPI LCD, ST7789 Controller             | Inexpensive generic full-color TFT display. Requires jumper cables to connect to the Pi header pins |
| `mock`       | No physical display                            | Simulates a display to `oled_preview.png` file. Used during development on PC |

TODO: Add links

## Automatic Setup

To facilitate the installation, we provide several scripts to allow you to install all necessary files on an SD card created with the [Raspberry Pi Imager](https://www.raspberrypi.com/software/). Here are the steps:

1. Use an SD card with a minimum of 4GB size and create your image using the Imager. Select your device, OS (select Lite), and your storage. Don't forget to set your Wi-Fi network and password, and make sure SSH is enabled. Use the flashed SD card to boot your Pi device and SSH into it.

2. Next we need to get the software from a GitHub repository. To do that, first install the `git` package on your device:

```
sudo apt-get install git
```
and then get the software:
```
git clone https://github.com/izivkov/gshock-server-dist.git
```

This will create a directory `gshock-server-dist` containing a number of shell scripts needed to set up the server. Note that running the scripts takes relativey long time. In the Pi 3/4, typically half an hour. On the Pi Zero, let it run overnight ;-). 

The scripts are described below:

### setup.sh

This script installs the basic software, dependencies, sets up a service to start the server each time the device is rebooted, etc. For a device with no display, this is sufficient to run the server.

### setup-display.sh
Installs all display-related dependencies. While installing, it will ask you to select the display type.

Note: You need to run both setup.sh and setup-display.sh.

### gshock-updater.sh

(Optional) This script will set the device to automatically update its software if a new version is available on GitHub. It will then restart the server, so you will always be running the latest version.

### enable-spi.sh
This script will enable the Linux driver needed for the display. Without this step, the display will not work. Reboot when asked after the script runs.

### setup-all.sh
Runs all the scripts above in one step.




## Troubleshooting
If your watch is not connecting, remove `config.ini` file and try again. 

To see output from the service do:
```
journalctl -u gshock.service -f
```




