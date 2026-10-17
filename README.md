# GShockTimeServer

GShockTimeServer automatically sets the correct time on compatible Casio G-Shock, Edifice, and Pro Trek watches over Bluetooth Low Energy. It is a small, headless Python service for computers with Bluetooth; it does not require a Raspberry Pi or include a user interface or display support.

## Project split

This repository is the generic headless time server and retains the `GShockTimeServer` name. Raspberry Pi installation, hardware integration, and display support have moved to the separate [GShockTimeServerPi project](https://github.com/izivkov/GShockTimeServerPi).

## Requirements

- Python 3.12 or newer
- Bluetooth Low Energy hardware and a supported Casio watch
- [`uv`](https://docs.astral.sh/uv/)

## Quick start

Install `uv` if needed:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create the environment and install dependencies:

```sh
uv sync
```

Start the server:

```sh
uv run src/gshock-server/gshock_server.py
```

Long-press the watch's lower-left button or short-press its lower-right button to connect. The server sets the watch time after a successful connection. Watches with automatic time adjustment enabled can connect on their own.

To apply a small time offset, pass `--fine-adjustment-secs` with a value from `-10` to `10`:

```sh
uv run src/gshock-server/gshock_server.py --fine-adjustment-secs 2
```

## Supported watch models

Compatibility depends on the watch module. Reported models include:

| Model | Module |
| --- | --- |
| GW-B5600 | 3461 |
| GM-B5600 / GMW-B5600 | 3459 |
| GMW-B5000 | 3459, 3461 |
| GW-5000 | 3159, 3495 |
| GA-B2100 | 5689 |
| GST-B500 | 5684 |
| GST-B200 | 5608 |
| MSG-B100 | 5659 |
| G-B001 | 3519 |
| GBD-800 | 3464 |
| GBD-H1000 | 3475 |
| MRG-B5000 | 3541 |
| GCW-B5000 | 3543 |
| GG-B100 | 5594, 5595 |
| ABL-100WE | 3565 |
| Edifice ECB-10 | 5618, 5604 |
| Edifice ECB-20 | 5638, 5603 |
| Edifice ECB-30 | 5686, 5672 |

Compatibility does not mean every watch function is supported; for example, fitness features are outside this project's scope. Please report model or module corrections in [Issues](https://github.com/izivkov/GShockTimeServer/issues).

## Notes

The server includes a filter that limits repeated connections from certain watches. For Raspberry Pi setup and display support, use the [GShockTimeServerPi project](https://github.com/izivkov/GShockTimeServerPi). For the smaller ESP32 implementation, see [gshock-api-esp32](https://github.com/izivkov/gshock-api-esp32).