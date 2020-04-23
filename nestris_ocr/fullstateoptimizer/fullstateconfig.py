from nestris_ocr.config import config


"""
Addition to configuration, with a few simple checks.
E.g. scan_field might be false, but if we are detecting flash via field,
we still need to scan it
"""

# Todo: define dependencies somewhere, and enforce in calibrate.py
# Is this class still necessary?


class FullStateConfiguration(object):
    def __init__(self, config):
        self.config = config
        self.capture_field = self.determine_capture_field(config)
        self.capture_stats = config["stats.enabled"]
        self.stats_method = config["stats.capture_method"]
        self.capture_preview = config["calibration.capture_preview"]
        self.capture_flash = self.determine_capture_flash(config)

    def determine_capture_field(self, config):
        if config["calibration.capture_field"]:
            return True
        elif config["calibration.flash_method"] == "FIELD":
            return True
        elif config["stats.enabled"] and config["stats.capture_method"] == "FIELD":
            return True

    def determine_capture_flash(self, config):
        return (
            config["calibration.flash_method"] == "FIELD"
            or config["calibration.flash_method"] == "BACKGROUND"
        )


FS_CONFIG = FullStateConfiguration(config)
