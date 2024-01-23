================
GShockTimeServer
================

Overview:
=========
This project allows you to set the correct time to your Casio G-Shock `B5600 <https://amzn.to/3Mt68Qb>`__ / `B5000 <https://amzn.to/4194M13>`_ / `B2100 <https://amzn.to/3MUDCGY>`__ watches.

In addition, this repository provides an API for developing application for the above watches. This is WIP,
but you can take a look at the ``api_tests.py`` file on how to use the API.

Usage:
======
This app can run on any device with Python and Bluetooth capabilities - from a desktop to a Raspberry Pi Zero. 
It has been tested on Linux OS only, but should be compatible with Windows as well.

1. Go to /src/gshocktimeserver directory.

2. run:

    **python3 gshock_server.py [--multi-watch]** (the --multi-watch parameter is used if you have multiple watches)

3. To set the time on your G-Shock, short-press the ``lower-right`` button and the watch will connect to the app, allowing the app to set the watch's time.

4. If AUTO TIME ADJUSTEMENT is enabled on the watch, it will sync up to 4 times daily with the app and adjust its time accordingly.


Installation:
=============
Install the following dependencies:

    pip3 install pytz

    pip3 install bleak
    
    pip3 install reactivex

Troubleshooting:
================
If your watch cannot connect, and the ``--multi-watch`` parameter is not used, remove the "config.ini" file and try again.

To Do:
======
We are working on a professional installation. 

