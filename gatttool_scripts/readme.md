# GATTTOOL Scripts
## Overview

gatttool is a bluez utility that can be used to easily interact with a Bluetooth Low Energy device.
It is considered as deprecated and replaced by bluetoothctl, but the latter is (to my opinion) more difficult to use
and less documentation is available.

gattool can be used as a shell command, for example :

Long press the bottom left button of a GShock GA-B2100 to enter in connect mode, then type in a terminal :

`$ gatttool -b <address> -t random --char-read -a 0x04`

with `<address>` being the mac address of the device, for example `D3:60:4F:9A:33:29`

The answer of this command is `43 41 53 49 4f 20 47 41 2d 42 32 31 30 30 00 00`

You can translate it with an hexadecimal converter like `xxd` :

```shell
$ echo "43 41 53 49 4f 20 47 41 2d 42 32 31 30 30 00 00" | xxd -r -p;echo
CASIO GA-B2100
```

If you want to set the time of the watch, you will have to issue multiple write requests and commands while the device is connected.
gatttool in command line will not work because when invoked it does three actions : connect to the device, issue the command then disconnect.

gatttool can be used interactively. The latter example could be done this way :

```shell
$ gatttool -b D3:60:4F:9A:33:29 -I -t random
[D3:60:4F:9A:33:29] connect
Attempting to connect to D3:60:4F:9A:33:29
Connection successful
[D3:60:4F:9A:33:29][LE]> char-write-cmd 0xc 10
Notification handle = 0x000e value: 10 29 33 9a 4f 60 d3 7f 04 03 0f ff ff ff ff 24 00 00 00
[D3:60:4F:9A:33:29][LE]> disconnect
[D3:60:4F:9A:33:29][LE]> quit
$ 
```

If you want to write a bash script to issue multiple commands to the watch, you will have to use a command line interaction tool like expect-lite.

The script setTime.exp provided here is an expect-lite script which read the time from the computer and send it to a Casio GShock GA-B2100 whit gatttool interactive mode.

## Dependencies

$ sudo apt install bluez expect-lite

## Usage

setTime.exp and encodeTime scripts should be in the same directory. Make them executable with :

```shell
$ chmod +x setTime.exp encodeTime
```

Find the MAC address of your watch

