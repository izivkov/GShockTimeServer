# GShockTimeServer

## Announcement

This project is now split into two separate repositories:

- **GShockTimeServer**
- **gashock_api**

The **GShockTimeServer** repository contains the server-side code for setting the time on your G-Shock watch.

The **gashock_api** repository can be found [here](https://github.com/izivkov/gshock_api), and contains the API for developing applications for these watches. Please refer to the **gashock_api** repository for the latest updates and documentation.

If you just like to include the API in your project, you can install it using pip:

```bash
pip install gashock-api
```

## Overview

GShockTimeServer allows you to set the correct time on your Casio G-Shock watches, including:

- [B5600](https://amzn.to/3Mt68Qb)
- [B5000](https://amzn.to/4194M13)
- [B2100](https://amzn.to/3MUDCGY)

Additionally, this repository provides a Python API library for developing applications for these watches.  
While still a work in progress, you can refer to the `api_tests.py` file for usage examples.

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
python3 src/gshock_server.py [--multi-watch]
```

The optional `--multi-watch` parameter allows you to connect if you have multiple watches.

## Troubleshooting
If your watch is not connecting, remove `config.ini` file and try again.

