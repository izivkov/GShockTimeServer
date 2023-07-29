# GATTTOOL Scripts

## Overview
Here we will see how to send and script commands to a Casio GShock GA-B2100 from the command line, using gatttool.

As an example, the script setTime.exp provided here read the time from the computer and send it to the watch.

All the procedures given here work on GNU-Linux operating systems.

gatttool is a bluez utility that can be used to easily interact with a Bluetooth Low Energy device.
It is considered deprecated and replaced by bluetoothctl, but the latter lack of documentation and is (to my opinion) more difficult to use.
gattool can be used as a shell command, for example :

Long press the bottom left button of the watch to enter in connect mode, then type in a terminal :

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
To send multiple commands between connect and disconnect, gatttool has to be used interactively. The latter example could be done this way :

```shell
$ gatttool -b D3:60:4F:9A:33:29 -I -t random
[D3:60:4F:9A:33:29] connect
Attempting to connect to D3:60:4F:9A:33:29
Connection successful
[D3:60:4F:9A:33:29][LE]> char-read-hnd 0x04
Characteristic value/descriptor: 43 41 53 49 4f 20 47 41 2d 42 32 31 30 30 00 00 
[D3:60:4F:9A:33:29][LE]> disconnect
[D3:60:4F:9A:33:29][LE]> quit
$ 
```
If you want to automate the process in a script, you will have to use a command line interaction tool like expect-lite.

The script `setTime.exp` provided here is an expect-lite script which read the time from the computer and send it to a Casio GShock GA-B2100, using gatttool interactive mode.

## Dependencies

You will need to install bluez and expect-lite packages. On Debian and derivatives (Ubuntu, Linux Mint,...), type :

$ sudo apt install bluez expect-lite

## Usage

setTime.exp and encodeTime scripts should be in the same directory. Make them executable with :

`$ chmod +x setTime.exp encodeTime`

Find the MAC address of your watch with `bluetoothctl scan on` and press bottom right key of the watch. You should have an answer like :

`[NEW] Device D3:60:4F:9A:33:29 CASIO GA-B2100`

Stop the discovery with <kbd>Ctrl</kbd><kbd>C</kbd>, then open `setTime.exp` and copy the MAC address in the line beginning with `$MAC=`

Launch the script with the command :

`$ .\setTime.exp`

then press bottom right key of the watch.

## References

* [Casio GA-B2100 protocol](/protocol.md)
* [gatttool Syntax and examples](http://tvaira.free.fr/flower-power/gatttool.txt)
* [Reading Values From a BLE Device](https://www.instructables.com/Reading-Values-From-a-BLE-Device-Using-CSR1010-and/)
* [Ivo Zivkov's GShock API](https://github.com/izivkov/GShockAPI)
* [Ivo Zivkov's GShock time server](https://github.com/izivkov/GShockTimeServer)
* [Gadgetbridge](https://codeberg.org/Freeyourgadget/Gadgetbridge)
 
