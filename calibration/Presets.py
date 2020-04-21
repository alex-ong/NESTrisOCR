from multiprocessing import cpu_count


# default standalone preset. Ideal for capturing
def preset_standalone(config):
    # 4 threads; score, lines, level, stats
    config["performance.num_threads"] = min(cpu_count(), 4)
    config["stats.enabled"] = True
    config["calibration.capture_preview"] = False
    config["calibration.capture_field"] = False
    config["stats.capture_method"] = "FIELD"
    config["network.host"] = "127.0.0.1"
    config["network.port"] = 3338
    config["network.protocol"] = "LEGACY"


# default das trainer preset. ideal for storing and recording das trainer
def preset_dastrainer_standalone(config):
    pass


# default nestris99 preset. ideal for streaming to internet.
def preset_nestris99(config):
    # 6 threads; board, score, lines, level, preview
    config["performance.num_threads"] = min(cpu_count(), 6)
    config["stats.enabled"] = False
    config["calibration.capture_field"] = True
    config["calibration.capture_preview"] = True
    config["network.host"] = "ec2-13-237-232-112.ap-southeast-2.compute.amazonaws.com"
    config["network.port"] = 3338
    config["network.protocol"] = "AUTOBAHN_V2"


def preset_none(config):
    return


presets = {
    "standalone": preset_standalone,
    "NESTris99": preset_nestris99,
    "": preset_none,
}
