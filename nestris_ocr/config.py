from cached_property import threaded_cached_property
from collections import OrderedDict
import json

from nestris_ocr.utils.sub_image import spawn_subimage

# fmt: off
CONFIG_DEFAULTS = {
    "player.name": "",
    "player.twitch_url": "",

    "performance.num_threads": 2,
    "performance.support_hex_score": True,
    "performance.support_hex_level": True,
    "performance.scan_rate": 30,
    "performance.capture_method": "DIRECT_CAPTURE",

    "stats.enabled": False,
    "stats.capture_method": "FIELD",

    "calibration.capture_method": "WINDOW",
    "calibration.source_id": "OBS",

    "calibration.flash_method": "BACKGROUND",
    # rgb limit of flash. Value above threshold is considered flash. Only used in BACKGROUND method
    "calibration.flash_threshold": 150,

    "calibration.game_coords": [0, 0, 1500, 1500],
    "calibration.pct.score": [0.75, 0.247, 0.184, 0.034],
    "calibration.pct.lines": [0.594, 0.069, 0.092, 0.035],
    "calibration.pct.level": [0.813, 0.713, 0.062, 0.035],
    "calibration.pct.stats": [0.187, 0.392, 0.091, 0.459],
    "calibration.pct.flash": [0.13, 0.111, 0.065, 0.004],

    # if capture_field, 2 primary colors will be needed
    "calibration.capture_field": False,
    "calibration.pct.field": [0.376, 0.175, 0.311, 0.72],
    "calibration.pct.color1": [0.151, 0.48, 0.018, 0.018],
    "calibration.pct.color2": [0.151, 0.554, 0.018, 0.018],

    "calibration.capture_preview": True,
    "calibration.pct.preview": [0.753, 0.5, 0.12, 0.064],

    "network.host": "127.0.0.1",
    "network.port": 3338,
    "network.protocol": "LEGACY",

    "debug.print_packet": True
}
# fmt: on
CONFIG_CHOICES = {
    "performance.num_threads": {1, 2, 3, 4, 5, 6, 7, 8},
    "performance.capture_method": {"DIRECT_CAPTURE", "WINDOW_N_SLICE"},
    "stats.capture_method": {"FIELD", "TEXT"},
    "calibration.capture_method": {"WINDOW", "OPENCV", "FILE"},
    "calibration.flash_method": {"FIELD", "BACKGROUND", "NONE"},
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
            # reset to default on parsing error
            self.data = OrderedDict(CONFIG_DEFAULTS)

    def __getitem__(self, key):
        if key not in CONFIG_DEFAULTS:
            raise KeyError("Invalid key")

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


config = Config("config.json")
