from config import config


"""
Addition to configuration, with a few simple checks.
E.g. scan_field might be false, but if we are detecting flash via field,
we still need to scan it
"""

# Todo: define dependencies somewhere, and enforce in calibrate.py


class FullStateConfiguration(object):
    def __init__(self, config):
        self.config = config
        self.capture_field = self.determine_capture_field(config)
        self.capture_stats = config.get("stats.enabled")
        self.stats_method = config.get("stats.capture_method")
        self.capture_preview = config.get("calibration.capture_preview")
        self.capture_flash = self.determine_capture_flash(config)

    def determine_capture_field(self, config):
        if config.get("calibration.capture_field"):
            return True
        elif config.get("calibration.flash_method") == "FIELD":
            return True
        elif (
            config.get("stats.enabled")
            and config.get("stats.capture_method") == "FIELD"
        ):
            return True

    def determine_capture_flash(self, config):
        return (
            config.get("calibration.flash_method") == "FIELD"
            or config.get("calibration.flash_method") == "BACKGROUND"
        )


FS_CONFIG = FullStateConfiguration(config)
