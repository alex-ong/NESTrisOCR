# invoke from root as python -m scripts.restream
import sys
from subprocess import Popen, PIPE
import time
import re

with open("config.stream.template.json", "r") as content_file:
    config_base_file = content_file.read()


RESOLUTIONS = {
    "1080": [1920, 1080],
    "720": [1280, 720],
    "480": [852, 480],
    "360": [640, 360],
}

CAP_RATIOS = [1233 / 1920, 1]  # based on the stencil dimensions for 1080p

PLAYER_SETTINGS = [
    [8081, 4001],
    [8082, 4002],
]


def setupPlayer(twitch_name, player_num):
    local_stream_port, ocr_dest_port = PLAYER_SETTINGS[player_num - 1]

    twitch_url = "twitch.tv/{}".format(twitch_name)
    local_url = "http://localhost:{}".format(local_stream_port)

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
            twitch_url,
            ",".join(resolutions),
            "--player",
            "vlc --intf dummy --sout '#standard{access=http,mux=mkv,dst=localhost:"
            + str(local_stream_port)
            + "}'",
        ]
    )

    time.sleep(10)

    p = Popen(["ffmpeg", "-i", local_url], stdout=PIPE, stderr=PIPE)

    stdout, stderr = p.communicate()

    fps_re = re.compile(", (?P<fps>[0-9.]+) tbr,")

    m = fps_re.search(str(stderr))

    try:
        fps = int(m.group("fps"))
    except Exception:
        fps = float(m.group("fps"))

    print("Found fps", fps)

    size_re = re.compile(", \\d+x(?P<size_key>(360|480|720|1080))(,| \\[SAR)")

    m = size_re.search(str(stderr))

    width, height = RESOLUTIONS[m.group("size_key")]

    print("Found size", width, height)

    # Update player config file
    player_config = (
        config_base_file.replace("USER_NAME", twitch_name)
        .replace("TWITCH_NAME", twitch_name)
        .replace("TWITCH_URL", twitch_url)
        .replace("STREAM_URL", local_url)
        .replace("PORT", str(ocr_dest_port))
        .replace("SCAN_RATE", str(fps))
        .replace("CAP_WIDTH", str(round(width * CAP_RATIOS[0])))
        .replace("CAP_HEIGHT", str(round(height * CAP_RATIOS[1])))
    )  # TODO read from ffmpeg instead

    player_config_filename = "config.competition.p{}.json".format(player_num)

    with open(player_config_filename, "w") as content_file:
        content_file.write(player_config)

    # Run calibrator on player stream
    p = Popen(["python3", "calibrate.py", "--config", player_config_filename])
    p.wait()

    # Run NESTrisOCR on player stream
    Popen(["python3", "main.py", "--config", player_config_filename])


if __name__ == "__main__":
    setupPlayer(sys.argv[1], int(sys.argv[2]))
