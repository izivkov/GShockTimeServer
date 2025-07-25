import time
import string


def to_casio_cmd(bytesStr):
    parts = [bytesStr[i: i + 2] for i in range(0, len(bytesStr), 2)]
    hexArr = [int(str, 16) for str in parts]
    return bytes(hexArr)


def to_int_array(hexStr):
    intArr = []
    strArray = hexStr.split(" ")
    for s in strArray:
        if s.startswith("0x"):
            s = s.replace("0x", "")
        intArr.append(int(s, 16))
    return intArr


def to_compact_string(hexStr):
    compactString = ""
    strArray = hexStr.split(" ")
    for s in strArray:
        if s.startswith("0x"):
            s = remove_prefix(s, "0x")
        compactString += s

    return compactString


def to_hex_string(byte_arr):
    return "0x" + " ".join(format(x, "02X") for x in byte_arr)


def remove_prefix(string, prefix):
    return string[len(prefix):] if string.startswith(prefix) else string


def to_ascii_string(hexStr, commandLengthToSkip):
    asciiStr = ""
    strArrayWithCommand = hexStr.split(" ")
    if len(strArrayWithCommand) == 1:  # no spaces between hex values, i.e. 4C4F4E444F4E
        strArrayWithCommand = [hexStr[i: i + 2] for i in range(0, len(hexStr), 2)]

    # skip command
    strArray = strArrayWithCommand[commandLengthToSkip:]
    asc = "".join(strArray)
    asciiStr = bytes.fromhex(asc).decode("ASCII")
    return asciiStr


def trimNonAsciiCharacters(string):
    return string.replace("\0", "")


def current_milli_time():
    return round(time.time() * 1000)


def clean_str(dirty_str):
    printable = set(string.printable)
    return "".join(filter(lambda x: x in printable, dirty_str))


def to_byte_array(string, maxLen):
    retArr = string.encode("utf-8")
    if len(retArr) > maxLen:
        return retArr[:maxLen]
    elif len(retArr) < maxLen:
        return retArr + bytearray(maxLen - len(retArr))
    else:
        return retArr


def to_hex_string_compact(asciiStr, maxLen):
    byteArr = bytearray(asciiStr, 'ascii')
    hexStr = ""
    for byte in byteArr:
        hexStr += "{:02x}".format(byte)
    return hexStr


def dec_to_hex(dec):
    return int(str(hex(dec))[2:])


def encode_string(ascii_string, maxlen):
    # Convert the ascii string into an array of integers
    int_arr = [ord(c) for c in ascii_string]

    # Pad the array up to maxlen with zeroes
    while len(int_arr) < maxlen:
        int_arr.append(0)

    # Convert the array back into a string
    hex_string = ''
    for i in int_arr:
        hex_string += '{:02X}'.format(i)

    return hex_string
