import os
from subprocess import Popen, PIPE
import argparse
import time
import re

from nestris_ocr.config_class import Config


TEMPLATE_FILE = "scripts/config.stream.template.json"

CAP_RATIOS = [1233 / 1920, 1]  # based on the stencil dimensions for 1080p

# entries as [VLC_BRODCAST_PORT, OCR_SEND_PORT]
PLAYER_SETTINGS = [
    [8081, 4001],
    [8082, 4002],
]


def setup_player(twitch_name, player_num, local_vlc=True):
    print("Setting up player", twitch_name, player_num, local_vlc)

    local_stream_port, ocr_dest_port = PLAYER_SETTINGS[player_num - 1]
    twitch_url = "twitch.tv/{}".format(twitch_name)

    fps = -1

    resolutions = [
        "720p",
        "480p",
        "360p",
        "720p60",
        "480p60",
        "1080p",
        "1080p60",
        "360p60",
    ]

    # ==================================
    # 1. run local restreamer over http

    if local_vlc:
        source_url = "http://localhost:{}".format(local_stream_port)

        Popen(
            [
                "streamlink",
                twitch_url,
                ",".join(resolutions),
                "--hds-live-edge",
                "1",
                "--hls-live-edge",
                "1",
                "--player",
                "vlc --intf dummy --sout '#standard{access=http,mux=mkv,dst=localhost:"
                + str(local_stream_port)
                + "}'",
            ]
        )

        time.sleep(10)

    else:
        p = Popen(
            ["streamlink", twitch_url, ",".join(resolutions), "--stream-url"],
            stdout=PIPE,
            stderr=PIPE,
        )

        stdout, stderr = p.communicate()

        source_url = stdout.decode("UTF-8").strip()

        if not source_url:
            raise Exception("No Stream found")

        print("Twitch UR found", source_url)

    # ==================================
    # 2. read stream details with ffmpeg
    p = Popen(["ffmpeg", "-i", source_url], stdout=PIPE, stderr=PIPE)

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

    # ==================================
    # 3. write player config file from template

    player_config_file = "config.competition.p{}.json".format(player_num)

    os.remove(player_config_file)

    config = Config(player_config_file, auto_save=False, default_config=TEMPLATE_FILE)

    config["player.name"] = twitch_name
    config["player.twitch_url"] = twitch_url
    config["performance.scan_rate"] = fps
    config["calibration.game_coords"] = [
        0,
        0,
        round(width * CAP_RATIOS[0]),
        round(height * CAP_RATIOS[1]),
    ]
    config["network.port"] = ocr_dest_port
    config["capture.source_id"] = source_url

    config.save()

    # ==================================
    # 4. Run calibrator on player stream
    p = Popen(["python3", "calibrate.py", "--config", player_config_file])
    p.wait()

    # ==================================
    # 5. Run NESTrisOCR
    Popen(["python3", "main.py", "--config", player_config_file])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--novlc",
        default=False,
        action="store_true",
        help="Don't run a local VLC server from the twitch stream",
    )
    parser.add_argument("twitch_name")
    parser.add_argument("player_num", type=int)
    args = parser.parse_args()

    setup_player(args.twitch_name, args.player_num, local_vlc=(not args.novlc))
