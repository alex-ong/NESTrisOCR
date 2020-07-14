# invoke from root as python -m scripts.restream
import sys
from subprocess import Popen, PIPE
import time
import re

with open("scripts/config.stream.template.json", "r") as content_file:
    config_base_file = content_file.read()


CAP_RATIOS = [1233 / 1920, 1]  # based on the stencil dimensions for 1080p

# entries as [VLC_BRODCAST_PORT, OCR_SEND_PORT]
PLAYER_SETTINGS = [
    [8081, 4001],
    [8082, 4002],
]


def setupPlayer(twitchName, playerNum):
    local_stream_port, ocr_dest_port = PLAYER_SETTINGS[playerNum - 1]

    twitchUrl = "twitch.tv/{}".format(twitchName)
    localUrl = "http://localhost:{}".format(local_stream_port)

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

    # run local restreamer over http
    Popen(
        [
            "streamlink",
            twitchUrl,
            ",".join(resolutions),
            "--player",
            "vlc --intf dummy --sout '#standard{access=http,mux=mkv,dst=localhost:"
            + str(local_stream_port)
            + "}'",
        ]
    )

    time.sleep(10)

    p = Popen(["ffmpeg", "-i", localUrl], stdout=PIPE, stderr=PIPE)

    stdout, stderr = p.communicate()

    fps_re = re.compile(", (?P<fps>[0-9.]+) tbr,")

    m = fps_re.search(str(stderr))

    try:
        fps = int(m.group("fps"))
    except Exception:
        fps = float(m.group("fps"))

    print("Found fps", fps)

    size_re = re.compile(", (?P<width>\\d+)x(?P<height>\\d+)(,| \\[SAR)")

    m = size_re.search(str(stderr))

    width = int(m.group("width"))
    height = int(m.group("height"))

    print("Found size", width, height)

    # Update player config file
    player_config = (
        config_base_file.replace("USER_NAME", twitchName)
        .replace("twitchName", twitchName)
        .replace("twitchUrl", twitchUrl)
        .replace("STREAM_URL", localUrl)
        .replace("PORT", str(ocr_dest_port))
        .replace("SCAN_RATE", str(fps))
        .replace("CAP_WIDTH", str(round(width * CAP_RATIOS[0])))
        .replace("CAP_HEIGHT", str(round(height * CAP_RATIOS[1])))
    )  # TODO read from ffmpeg instead

    player_config_filename = "config.competition.p{}.json".format(playerNum)

    with open(player_config_filename, "w") as content_file:
        content_file.write(player_config)

    # Run calibrator on player stream
    p = Popen(["python3", "calibrate.py", "--config", player_config_filename])
    p.wait()

    # Run NESTrisOCR on player stream
    Popen(["python3", "main.py", "--config", player_config_filename])


if __name__ == "__main__":
    setupPlayer(sys.argv[1], int(sys.argv[2]))
