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

Virtual Environment Setup
=========================
To run the server in a virtual environment:

1. Create a virtual environment:

.. code-block:: sh

   # Create a virtual environment
   python -m venv myenv

   # Activate it (Mac/Linux)
   source myenv/bin/activate

   # Install dependencies
   pip install -e .

2. Run the server:

.. code-block:: sh

   python3 src/examples/gshock_server.py

3. Run the tests:

.. code-block:: sh

   python3 src/examples/api_tests.py

Troubleshooting:
================
If your watch cannot connect, and the 
`--multi-watch` parameter is not used, remove the `config.ini` file and try again.