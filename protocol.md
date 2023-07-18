# GShock GAB-2100 BLE protocol
## Commands
### Read (char-read-hnd)
0x4 : watch name

0x6 : device type

0x9 : TX Power level

### Write command (char-write-cmd)
#### 0xc
* 10 : Get button pressed
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
  
2-3 : city numéric identifier
  
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
