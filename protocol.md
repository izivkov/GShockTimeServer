# GShock GAB-2100 BLE protocol

## Overview
Casio bluetooth watches protocol has not been published by the constructor. The following description comes from experiments on the watch and analysis of the code of open source softwares dedicated to communicate with these watches :
* [Ivo Zivkov's GShock API](https://github.com/izivkov/GShockAPI)
* [Ivo Zivkov's GShock time server](https://github.com/izivkov/GShockTimeServer)
* [Gadgetbridge](https://codeberg.org/Freeyourgadget/Gadgetbridge)
* [Gadgetbridge time zone description](https://codeberg.org/johannesk/Gadgetbridge/src/branch/casio-gw-b5600/app/src/main/java/nodomain/freeyourgadget/gadgetbridge/service/devices/casio/gwb5600/CasioGWB5600TimeZone.java)

Syntax and examples come from [gatttool](http://tvaira.free.fr/flower-power/gatttool.txt).

## Commands
### Read (char-read-hnd)
* 0x4 : watch name
* 0x6 : device type
* 0x9 : TX Power level

### Write command (char-write-cmd)
#### 0xc
* 10 : Get button pressed (and other informations ?)
* 22 : Get app info
* 1D00 : Get time zones and DST state of watch
* 1e00 : Get local time zone parameters
* 1e01 : Get WT time zone parameters
* 1f00 : Get local time zone name
* 1f01 : Get WT time zone name

### Write request (char-write-req)
#### 0xe
* 1D00... : Set time zones and DST state of watch
* 1e00... : Set local time zone parameters
* 1e01... : Set WT time zone parameters
* 1f00... : Set local time zone name
* 1f01... : Set WT time zone name

#### 0xf
* 100 : ?

## Data packets

### 10 : button pressed
```
0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18
10 29 33 9a 4f 60 d3 7f 04 03 0f ff ff ff ff 24 00 00 00
```
8 : 04 : RIGHT BUTTON, 01 : LEFT BUTTON


### 1D00 : time zones and DST state of watch

```
0  1  2  3  4  5  6  7  8  9  10 11 12 13 14
1d 00 01 02 03 5b 00 dc 00 ff ff ff ff ff ff
```

0 : 1d

1 : local TZ index

2 : WT TZ index

3 : local TZ DST :
* 02 : No DST
* 03 : DST

4 : WT TZ DST

5-6 : 2 bytes integer (little-endian) : local City numeric identifier = b06 × 256 + b05 

7-8 : WT city numeric identifier

### 1E : Time zone parameters

```
0  1  2  3  4  5  6 
1e 01 52 00 16 04 00
```

0 : 1e

1 : TZ index :

* 00 : local
* 01 : WT
  
2-3 : city numeric identifier
  
4 : signed byte : time difference in quarter of an hour (divide by 4 to get it in hour)

5 : DST offset in quarter of hour : 00 for UTC and 04 for other TZ

6 : DST rules ? :

* 00 : UTC and cities without DST
* 01 : USA cities
* 02 : European cities (LON, PAR, ATH)
* 04 : Australia
* 05 : New Zealand (Wellington)
* 12 : Lord Howe Island
* 17 : Chatam Islands
* 2b : Teheran

## Examples with gatttool
### Installation
gatttool is part of the bluez package. On Debian and derivatives, it could be installed with :

`sudo apt install bluez`

### gatttool usage

Gatttool syntax with examples is described [here](http://tvaira.free.fr/flower-power/gatttool.txt).

Beware of handle and data values, gatttool documentation is confusing. Write command syntax in interactive mode is :

`char-write-cmd <handle> <data>`

* Handle value should be writen in hexadecimal base with 0x prefix.
* Data value should be writen in hexadecimal base **without** 0x prefix.

Example : `char-write-cmd 0xc 1d00`

In non interactive mode, the syntax is :

`gatttool -b <address> --char-write-req -a <handle> -n <data> --listen`

Here handle value can be written either in hexadecimal with prefix or decimal, but data value should be in hexadecimal base **without** prefix.

### Examples

```shell
$ gatttool -b D3:60:4F:9A:33:29 -I -t random
[D3:60:4F:9A:33:29]      connect
Attempting to connect to D3:60:4F:9A:33:29
Connection successful
[D3:60:4F:9A:33:29][LE]> char-write-cmd 0xc 10
Notification handle = 0x000e value: 10 29 33 9a 4f 60 d3 7f 04 03 0f ff ff ff ff 24 00 00 00
[D3:60:4F:9A:33:29][LE]> char-read-hnd 0x04
Characteristic value/descriptor: 43 41 53 49 4f 20 47 41 2d 42 32 31 30 30 00 00 
[D3:60:4F:9A:33:29][LE]> disconnect
[D3:60:4F:9A:33:29][LE]> quit
```

## Character table

The GAB-2100 character table is a mix of [ASCII](https://en.wikipedia.org/wiki/ASCII) and [JIS X 0201](https://en.wikipedia.org/wiki/JIS_X_0201) with additions:


|       | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | a | b | c | d | e | f |
|-------|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **0** |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| **1** |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |   |
| **2** |   |   |   | # | $ | % | & | ' | ( | ) | * | + | , |---| . | / |
| **3** | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | : | ; | < | = | > | ? |
| **4** | @ | A | B | C | D | E | F | G | H | I | J | K | L | M | N | O |
| **5** | P | Q | R | S | T | U | V | W | X | Y | Z | [ | \ | ] | ^ | _ |
| **6** | ` | a | b | c | d | e | f | g | h | i | j | k | l | m | n | o |
| **7** | p | q | r | s | t | u | v | w | x | y | z | { | \| | } | ~ |   |
| **8** | ¥ | ╏ | « | ¬ |---| ⎺ | ° | ± | ´ | · | ¸ | » | ♦ | ♪ | ■ | < |
| **9** | 【 | 】| ◀ | ▶ | √ | y |   |   |   |   |   |   |   |   |   |   |
| **a** | . | ｡ | ｢ | ｣  | ､ | ･ | ｦ | ｧ | ｨ  | ｩ | ｪ | ｫ | ｬ | ｭ | ｮ  | ｯ | 
| **b** | ｰ  | ｱ  | ｲ  | ｳ  | ｴ  | ｵ  | ｶ  | ｷ  | ｸ  | ｹ  | ｺ  | ｻ  | ｼ  | ｽ  | ｾ  | ｿ |
| **c** | ﾀ  | ﾁ  | ﾂ  | ﾃ  | ﾄ  | ﾅ  | ﾆ  | ﾇ  | ﾈ  | ﾉ  | ﾊ  | ﾋ  | ﾌ  | ﾍ  | ﾎ  | ﾏ |
| **d** | ﾐ  | ﾑ  | ﾒ  | ﾓ  | ﾔ  | ﾕ  | ﾖ  | ﾗ  | ﾘ  | ﾙ  | ﾚ  | ﾛ  | ﾜ  | ﾝ  | ~ | ▫ |
| **e** | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| **f** | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |

To be completed :
- empty cells are non used blocks
- dots are fields to be completed.

 ## City list

 | Index | HB | LB | NAME | OFFSET | DST_OFFSET | DST_RULE |
| ------|----|----|------|--------|------------|----------|
| 313 | 1 | 39 | BAKER_ISLAND | -12 | 1 | 00 |
| 215 | 0 | D7 | PAGO_PAGO | -11 | 1 | 00 |
| 123 | 0 | 7B | HONOLULU | -10 | 1 | 00 |
| 314 | 1 | 3A | MARQUESAS_ISLANDS | -9.5 | 1 | 00 |
| 12 | 0 | 0C | ANCHORAGE | -9 | 1 | 01 |
| 161 | 0 | A1 | LOS_ANGELES | -8 | 1 | 01 |
| 84 | 0 | 54 | DENVER | -7 | 1 | 01 |
| 66 | 0 | 42 | CHICAGO | -6 | 1 | 01 |
| 202 | 0 | CA | NEW_YORK | -5 | 1 | 01 |
| 113 | 0 | 71 | HALIFAX | -4 | 1 | 01 |
| 268 | 1 | 0C | ST.JOHN'S | -3.5 | 1 | 01 |
| 241 | 0 | F1 | RIO_DE_JANEIRO | -3 | 1 | 00 |
| 98 | 0 | 62 | F.DE_NORONHA | -2 | 1 | 00 |
| 233 | 0 | E9 | PRAIA | -1 | 1 | 00 |
| 0 | 0 | 00 | UTC | 0 | 0 | 00 |
| 160 | 0 | A0 | LONDON | 0 | 1 | 02 |
| 220 | 0 | DC | PARIS | 1 | 1 | 02 |
| 19 | 0 | 13 | ATHENS | 2 | 1 | 02 |
| 133 | 0 | 85 | JEDDAH | 3 | 1 | 00 |
| 278 | 1 | 16 | TEHRAN | 3.5 | 1 | 2B |
| 91 | 0 | 5B | DUBAI | 4 | 1 | 00 |
| 136 | 0 | 88 | KABUL | 4.5 | 1 | 00 |
| 139 | 0 | 8B | KARACHI | 5 | 1 | 00 |
| 82 | 0 | 52 | DELHI | 5.5 | 1 | 00 |
| 140 | 0 | 8C | KATHMANDU | 5.75 | 1 | 00 |
| 86 | 0 | 56 | DHAKA | 6 | 1 | 00 |
| 303 | 1 | 2F | YANGON | 6.5 | 1 | 00 |
| 28 | 0 | 1C | BANGKOK | 7 | 1 | 00 |
| 122 | 0 | 7A | HONG_KONG | 8 | 1 | 00 |
| 234 | 0 | EA | PYONGYANG | 9 | 1 | 00 |
| 310 | 1 | 36 | EUCLA | 8.75 | 1 | 00 |
| 281 | 1 | 19 | TOKYO | 9 | 1 | 00 |
| 5 | 0 | 05 | ADELAIDE | 9.5 | 1 | 04 |
| 271 | 1 | 0F | SYDNEY | 10 | 1 | 04 |
| 311 | 1 | 37 | LORD_HOWE_ISLAND | 10.5 | 0.5 | 12 |
| 205 | 0 | CD | NOUMEA | 11 | 1 | 00 |
| 299 | 1 | 2B | WELLINGTON | 12 | 1 | 05 |
| 63 | 0 | 3F | CHATHAM_ISLANDS | 12.75 | 1 | 17 |
| 208 | 0 | D0 | NUKUALOFA | 13 | 1 | 00 |
| 147 | 0 | 93 | KIRITIMATI | 14 | 1 | 00 |

