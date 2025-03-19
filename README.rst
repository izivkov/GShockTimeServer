GShockTimeServer
================

Overview
========
GShockTimeServer allows you to set the correct time on your Casio G-Shock watches, including:

- `B5600 <https://amzn.to/3Mt68Qb>`__
- `B5000 <https://amzn.to/4194M13>`__
- `B2100 <https://amzn.to/3MUDCGY>`__

Additionally, this repository provides an API for developing applications for these watches.  
While still a work in progress, you can refer to the ``api_tests.py`` file for usage examples.

Usage
=====
This app can run on any device with Python and Bluetooth capabilities—from a desktop to a Raspberry Pi Zero.  
It has been tested on Linux but should also work on Windows.

.. image:: images/pizero.jpg
   :alt: Pi Zero Running the Server
   :align: center

Setting the Time
----------------
1. Ensure the app is running on your device.
2. Short-press the **lower-right** button on your G-Shock watch to connect.
3. Once connected, the app will automatically set the correct time on your watch.
4. If **AUTO TIME ADJUSTMENT** is enabled, the watch will sync up to **four times daily**.

Dependencies
============

This project requires the following Python packages:
```
pytz
bleak
gashock-api
```

So you can install them using the following command:
```
pip3 install -r requirements.txt
```

Then run:
```
   python3 src/gshock_server.py [--multi-watch]
```   

The optional **`--multi-watch`** parameter allows you to connect if you have multiple watches.
