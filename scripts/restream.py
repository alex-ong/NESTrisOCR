import sys
from subprocess import Popen, PIPE
import time
import re
import json


TEMPLATE_FILE = "scripts/config.stream.template.json"

CAP_RATIOS = [1233 / 1920, 1]  # based on the stencil dimensions for 1080p

# entries as [VLC_BRODCAST_PORT, OCR_SEND_PORT]
PLAYER_SETTINGS = [
    [8081, 4001],
    [8082, 4002],
]


def setupPlayer(twitchName, playerNum):
    localStreamPort, ocrDestPort = PLAYER_SETTINGS[playerNum - 1]

    twitchUrl = "twitch.tv/{}".format(twitchName)
    localUrl = "http://localhost:{}".format(localStreamPort)

    fps = -1

    resolutions = [
        "720p",
        "480p",
        "360p",
        "720p60",
        "480p60",
        "1080p",
        "1080p60",
    ]

    # ==================================
    # 1. run local restreamer over http
    Popen(
        [
            "streamlink",
            twitchUrl,
            ",".join(resolutions),
            "--player",
            "vlc --intf dummy --sout '#standard{access=http,mux=mkv,dst=localhost:"
            + str(localStreamPort)
            + "}'",
        ]
    )

    time.sleep(10)

    # ==================================
    # 2. read stream details with ffmpeg
    p = Popen(["ffmpeg", "-i", localUrl], stdout=PIPE, stderr=PIPE)

    stdout, stderr = p.communicate()

    fpsRegex = re.compile(", (?P<fps>[0-9.]+) tbr,")

    m = fpsRegex.search(str(stderr))

    try:
        fps = int(m.group("fps"))
    except Exception:
        fps = float(m.group("fps"))

    print("Found fps", fps)

    sizeRegex = re.compile(", (?P<width>\\d+)x(?P<height>\\d+)(,| \\[SAR)")

    m = sizeRegex.search(str(stderr))

    width = int(m.group("width"))
    height = int(m.group("height"))

    print("Found size", width, height)

    # ==================================
    # 3. write player config file from template

    # Not using the Config class because it requires CLI args
    # which are too much for this tiny script

    playerConfigFile = "config.competition.p{}.json".format(playerNum)

    with open(TEMPLATE_FILE) as jsonFile:
        config = json.load(jsonFile)

    config["player.name"] = twitchName
    config["player.twitch_url"] = twitchUrl
    config["performance.scan_rate"] = fps
    config["calibration.game_coords"] = [
        0,
        0,
        round(width * CAP_RATIOS[0]),
        round(height * CAP_RATIOS[1]),
    ]
    config["network.port"] = ocrDestPort
    config["capture.source_id"] = localUrl

    with open(playerConfigFile, "w") as jsonFile:
        json.dump(config, jsonFile)

    # ==================================
    # 4. Run calibrator on player stream
    p = Popen(["python3", "calibrate.py", "--config", playerConfigFile])
    p.wait()

    # ==================================
    # 5. Run NESTrisOCR
    Popen(["python3", "main.py", "--config", playerConfigFile])


if __name__ == "__main__":
    setupPlayer(sys.argv[1], int(sys.argv[2]))
