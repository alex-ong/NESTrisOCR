import argparse
from cached_property import threaded_cached_property
from collections import OrderedDict
import json

from nestris_ocr.utils.sub_image import spawn_subimage

# fmt: off
CONFIG_DEFAULTS = {
    "player.name": "",
    "player.twitch_url": "",

    "calibrator.ui": "SIMPLE",

    "performance.support_hex_score": True,
    "performance.support_hex_level": True,
    "performance.scan_rate": 30,

    "stats.enabled": False,
    "stats.capture_method": "FIELD",

    # related to getting the base image for ocr
    "capture.method": "WINDOW",
    "capture.source_id": "OBS",
    "capture.source_extra_data" : "",
    "capture.deinterlace_method": "DISCARD_BOTTOM",
    "capture.deinterlace_res": "FULL",
    "calibration.palette": "DEFAULT",

    "calibration.flash_method": "NONE",
    # rgb limit of flash. Value above threshold is considered flash. Only used in BACKGROUND method
    "calibration.flash_threshold": 150,

    "calibration.game_coords": [0, 0, 1500, 1500],
    "calibration.pct.score": [0.751, 0.252, 0.185, 0.030],
    "calibration.pct.lines": [0.595, 0.074, 0.088, 0.030],
    "calibration.pct.level": [0.814, 0.717, 0.057, 0.030],
    "calibration.pct.stats": [0.187, 0.392, 0.091, 0.459],
    "calibration.pct.flash": [0.749, 0.370, 0.07, 0.012],

    # if capture_field, 2 primary colors will be needed
    "calibration.capture_field": True,
    "calibration.pct.field": [0.376, 0.175, 0.311, 0.72],

    "calibration.dynamic_colors": True,
    "calibration.pct.color1": [0.151, 0.48, 0.018, 0.018],
    "calibration.pct.color2": [0.151, 0.554, 0.018, 0.018],

    "calibration.dynamic_black_n_white": True,
    "calibration.color_interpolation": True,
    "calibration.pct.black_n_white": [0.827, 0.431, 0.028, 0.02],

    "calibration.capture_preview": True,
    "calibration.pct.preview": [0.753, 0.5, 0.12, 0.064],

    "calibration.capture_das": False,
    "calibration.pct.das.current_piece": [0.060, 0.191, 0.09, 0.059],
    "calibration.pct.das.current_piece_das": [0.216, 0.211, 0.061, 0.034],
    "calibration.pct.das.instant_das": [0.154, 0.134, 0.061, 0.034],

    "network.host": "127.0.0.1",
    "network.port": 3338,
    "network.protocol": "LEGACY",

    "debug.print_packet": True,
    "debug.print_benchmark": False
}
# fmt: on
CONFIG_CHOICES = {
    "calibrator.ui": {"SIMPLE", "ADVANCED"},
    "stats.capture_method": {"FIELD", "TEXT"},
    "capture.method": {"WINDOW", "OPENCV", "FILE"},
    "calibration.flash_method": {"FIELD", "BACKGROUND", "NONE"},
    "capture.deinterlace_method": {
        "NONE",
        "DISCARD_TOP",
        "DISCARD_BOTTOM",
        "TOP_FIRST",
        "BOTTOM_FIRST",
    },
    "capture.deinterlace_res": {"FULL", "HALF"},
    "network.protocol": {"LEGACY", "FILE", "AUTOBAHN", "AUTOBAHN_V2"},
}


class Config:
    def __init__(self, path, auto_save=True):
        self.path = path
        self.auto_save = auto_save
        try:
            with open(path, "r") as file:
                self.data = json.load(file, object_pairs_hook=OrderedDict)
        except Exception:
            # override with default on non-existent file or parsing error
            self.data = OrderedDict(CONFIG_DEFAULTS)
            self.save()

    def __getitem__(self, key):
        if key not in CONFIG_DEFAULTS:
            raise KeyError("Invalid key %s" % (key,))

        return self.data.get(key, CONFIG_DEFAULTS[key])

    def __setitem__(self, key, value):
        if key not in CONFIG_DEFAULTS:
            raise KeyError("Invalid key")

        if key in CONFIG_CHOICES:
            if value not in CONFIG_CHOICES[key]:
                raise ValueError("Invalid value. Not allowed by CONFIG_CHOICES")

        # fmt: off
        default = CONFIG_DEFAULTS[key]
        if (
            isinstance(default, int) and not isinstance(value, int)
            or isinstance(default, float) and not isinstance(value, float)
            or isinstance(default, str) and not isinstance(value, str)
            or isinstance(default, list) and not (isinstance(value, list) or isinstance(value, tuple))
        ):
            raise TypeError("Invalid type. Check CONFIG_DEFAULTS for the type to use")
        # fmt: on

        self.data[key] = value

        if key == "calibration.pct.field":
            self.__dict__.pop("stats2_percentages", None)

        if self.auto_save:
            self.save()

    def save(self):
        with open(self.path, "w") as file:
            json.dump(self.data, file, indent=2)

    @threaded_cached_property
    def stats2_percentages(self):
        return spawn_subimage(self["calibration.pct.field"])


# Should probably be in main.py and calibrate.py
# But works fine here to extract just one arg
parser = argparse.ArgumentParser()
parser.add_argument("--config", default="config.json")
args = parser.parse_args()
config_filename = args.config

config = Config(config_filename)
