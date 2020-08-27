# default standalone preset. Ideal for capturing stats only
def preset_standalone(config):
    # score, lines, level, stats
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


# default nestris99 preset. ideal for connecting to n99 client
def preset_nestris99(config):
    # board, score, lines, level, preview
    config["stats.enabled"] = False
    config["calibration.capture_field"] = True
    config["calibration.capture_preview"] = True
    config["calibraiton.capture_line_clear"] = True
    config["network.host"] = "localhost"
    config["network.port"] = 3338
    config["network.protocol"] = "WEBSOCKET_SERVER"


def preset_none(config):
    return


presets = {
    "standalone": preset_standalone,
    "NESTris99": preset_nestris99,
    "": preset_none,
}
