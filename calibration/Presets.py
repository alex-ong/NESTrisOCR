from multiprocessing import cpu_count


# default standalone preset. Ideal for capturing
def preset_standalone(config):
    config.set(
        "performance.num_threads", min(cpu_count(), 4)
    )  # 4 threads; score, lines, level, stats
    config.config.set("stats.enabled", True)
    config.set("calibration.capture_preview", False)
    config.set("calibration.capture_field", False)
    config.set("stats.capture_method", "FIELD")
    config.set("network.host", "127.0.0.1")
    config.set("network.port", 3338)
    config.set("network.protocol", "LEGACY")


# default das trainer preset. ideal for storing and recording das trainer
def preset_dastrainer_standalone(config):
    pass


# default nestris99 preset. ideal for streaming to internet.
def preset_nestris99(config):
    config.set(
        "performance.num_threads", min(cpu_count(), 6)
    )  # 6 threads; board, score, lines, level, preview
    config.config.set("stats.enabled", False)
    config.set("calibration.capture_field", True)
    config.set("calibration.capture_preview", True)
    config.set(
        "network.host", "ec2-13-237-232-112.ap-southeast-2.compute.amazonaws.com"
    )
    config.set("network.port", 3338)
    config.set("network.protocol", "AUTOBAHN_V2")


def preset_none(config):
    return


presets = {
    "standalone": preset_standalone,
    "NESTris99": preset_nestris99,
    "": preset_none,
}
