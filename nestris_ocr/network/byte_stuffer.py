import json
import struct
import random

try:
    # todo: rename to native_bytestuffer
    from nestris_ocr.network.native_fieldpacker import prePackField

    # print ("loaded compiled prePackField")
except ImportError:
    from nestris_ocr.network.field_packer import prePackField

    print(
        "Warning: loaded non-compiled prePackField, please run buildByteStuffer2.py to make a compiled version"
    )

# this function converts a python dict to bytes for a small packet
# to transfer across the network

# 11 + 21 + 200 +1 + 10

SCORE = 0  # needs to support 0-F * 6 and null
LINES = 1  # needs to support 0-9 * 3 and null
LEVEL = 2  # needs to support 0-F * 2 and null
STATS = 3  # needs to support 0-9 * 3 and null for 7 pieces.
FIELD = 4  # needs to support 0-4 * 200 cells. 4 bits * 200 = 100 bytes
PREVIEW = 5  # needs to support 7 types + null, so can fit into a byte
TIME = 6  # 4 byte floating point.
GAMEID = 7  # 1 byte.
PLAYERNAME = 8  # ascii only; 10 chars?


SCORE_OFFSET = 3
LINES_OFFSET = 2
LEVEL_OFFSET = 2
STATS_OFFSET = LINES_OFFSET * 7
FIELD_OFFSET = 50
PREVIEW_OFFSET = 1
TIME_OFFSET = 4
GAMEID_OFFSET = 1

stats_order = "TJZOSLI"


# for use with AutoBahn server to detect player name.
def getPlayerOffset(byte_header):
    result = 2  # header size
    if byte_header & (1 << SCORE):
        result += SCORE_OFFSET
    if byte_header & (1 << LINES):
        result += LINES_OFFSET
    if byte_header & (1 << LEVEL):
        result += LEVEL_OFFSET
    if byte_header & (1 << STATS):
        result += STATS_OFFSET
    if byte_header & (1 << FIELD):
        result += FIELD_OFFSET
    if byte_header & (1 << PREVIEW):
        result += PREVIEW_OFFSET
    if byte_header & (1 << TIME):
        result += TIME_OFFSET
    if byte_header & (1 << GAMEID):
        result += GAMEID_OFFSET

    return result


def calculateMask(startdict):
    result = 0
    if "score" in startdict:
        result += 1 << SCORE
    if "lines" in startdict:
        result += 1 << LINES
    if "level" in startdict:
        result += 1 << LEVEL
    if "T" in startdict:
        result += 1 << STATS
    if "field" in startdict:
        result += 1 << FIELD
    if "preview" in startdict:
        result += 1 << PREVIEW
    if "time" in startdict:
        result += 1 << TIME
    if "gameid" in startdict:
        result += 1 << GAMEID
    if "playername" in startdict:
        result += 1 << PLAYERNAME

    return result


INFO_MASK = None


def stuffDictionary(input):
    global INFO_MASK
    if INFO_MASK is None:
        INFO_MASK = calculateMask(input)
    result = bytearray()

    result.extend(struct.pack(">H", INFO_MASK))

    if INFO_MASK & (1 << SCORE):
        result.extend(packScore(input["score"]))
    if INFO_MASK & (1 << LINES):
        result.extend(packLines(input["lines"]))
    if INFO_MASK & (1 << LEVEL):
        result.extend(packLevel(input["level"]))
    if INFO_MASK & (1 << STATS):
        result.extend(packStats(input))
    if INFO_MASK & (1 << FIELD):
        result.extend(packField(input["field"]))
    if INFO_MASK & (1 << PREVIEW):
        result.extend(packPreview(input["preview"]))
    if INFO_MASK & (1 << TIME):
        result.extend(packTime(input["time"]))
    if INFO_MASK & (1 << GAMEID):
        result.extend(packGameID(input["gameid"]))
    if INFO_MASK & (1 << PLAYERNAME):
        result.extend(packPlayer(input["playername"]))

    return result


def packScore(scoreString):
    if scoreString is None:
        return (16777215).to_bytes(3, "big", signed=False)

    startValue = scoreString[0]
    if startValue in "ABCDEF":
        hundred_k = ord(startValue) - ord("A") + 10
    else:
        hundred_k = int(startValue)
    hundred_k *= 100000
    rest = scoreString[1:]
    result = hundred_k + int(rest)
    return result.to_bytes(3, "big", signed=False)


# needs to take 000 -> 999 and null
def packLines(linesString):
    result = bytearray()
    if linesString is None:
        result = (1000).to_bytes(2, "big", signed=False)
    else:
        try:
            result = int(linesString)
            result = result.to_bytes(2, "big", signed=False)
        except Exception:
            result = (1000).to_bytes(2, "big", signed=False)
    return result


# store in two bytes.
# first byte is whether we are null
# second byte split as 4 bits (first char), 4 bits(2nd char)
def packLevel(levelString):
    result = bytearray()
    if levelString is None:
        result.append(255)
        result.append(255)
    else:
        first = hexToNibble(levelString[0])
        second = hexToNibble(levelString[1])
        result.append(first)
        result.append(second)
    return result


def hexToNibble(character):
    if character in "ABCDEF":
        return ord(character) - ord("A") + 10
    else:
        return ord(character) - ord("0")


def packStats(dataDict):
    result = bytearray()
    for letter in stats_order:
        result.extend(packLines(dataDict[letter]))
    return result


# this function is incredibly slow; json.dumps is 0.040 for 10000 iterations; this is 0.7
# even just allocating bytearray is so slow, taking 0.004
# allocating a 200 element python array takes 0.1
# it takes roughly 1ms at the moment.
def packField(data):
    if len(data) == FIELD_OFFSET:
        return data
    result = bytearray(FIELD_OFFSET)
    four_byte_counter = 0
    currentByte = 0
    index = 0
    for letter in data:
        currentByte += ord(letter) - ord("0")
        four_byte_counter += 1
        if four_byte_counter == 4:
            result[index] = currentByte
            four_byte_counter = 0
            currentByte = 0
            index += 1
        currentByte = currentByte << 2

    return result


def packPreview(letter):
    if letter is not None and letter in stats_order:  # faster than try/catch
        index = stats_order.index(letter)
    else:
        index = 7
    return index.to_bytes(1, "big", signed=False)


def packTime(timefloat):
    return struct.pack(">f", timefloat)


def packGameID(gameid):
    gameid = int(gameid) % 0x100
    return struct.pack(">B", gameid)


# one byte per item
PLAYER_NAME = None


def packPlayer(player):
    global PLAYER_NAME
    if PLAYER_NAME is None:
        try:
            playerEncoded = player.encode("ascii")
        except Exception:
            playerEncoded = ("sore_loser_" + str(random.randint(100, 10000))).encode(
                "ascii"
            )
        length = (len(playerEncoded)).to_bytes(1, "big")
        PLAYER_NAME = length + playerEncoded
    return PLAYER_NAME


if __name__ == "__main__":
    import numpy as np

    temp = {
        "playername": "²fluffy",
        "score": "008055",
        "lines": "015",
        "level": "01",
        "field": "03300000000133000000110000000011000000001100000000110000330021222233002223233310223333311022333331102233333330221133113022111111301222113330121133111012213311201123331120111331122021123111102212333110",
        "preview": "L",
        "time": 118.7786123752594,
    }
    raw_data = temp["field"]
    data = np.zeros((20, 10), dtype=np.uint8)
    packed = prePackField(data)
    temp["field"] = packed

    # temp = {"playername": "²fluffy", "score": "008055", "lines": "015", "level": "01", "preview": "L", "time": 118.7786123752594}
    stuffed = stuffDictionary(temp)
    print(stuffed)
    import time

    t = time.time()
    for i in range(10000):
        packField(raw_data)
    print(time.time() - t)

    t = time.time()
    for i in range(10000):
        json.dumps(raw_data)
    print(time.time() - t)

    t = time.time()
    for i in range(10000):
        prePackField(data)
    print(time.time() - t)
