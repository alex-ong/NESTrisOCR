from multiprocessing import cpu_count


# default standalone preset. Ideal for capturing
def preset_standalone(config):
    config.setThreads(min(cpu_count(), 4))  # 4 threads; score, lines, level, stats
    config.setCaptureStats(True)
    config.setCapturePreview(False)
    config.setCaptureField(False)
    config.setStatsMethod("FIELD")
    config.setHost("127.0.0.1")
    config.setPort(3338)
    config.setNetProtocol("LEGACY")


# default das trainer preset. ideal for storing and recording das trainer
def preset_dastrainer_standalone(config):
    pass


# default nestris99 preset. ideal for streaming to internet.
def preset_nestris99(config):
    config.setThreads(
        min(cpu_count(), 6)
    )  # 6 threads; board, score, lines, level, preview
    config.setCaptureStats(False)
    config.setCaptureField(True)
    config.setCapturePreview(True)
    config.setHost("ec2-13-237-232-112.ap-southeast-2.compute.amazonaws.com")
    config.setPort(3338)
    config.setNetProtocol("AUTOBAHN_V2")


def preset_none(config):
    return


presets = {
    "standalone": preset_standalone,
    "NESTris99": preset_nestris99,
    "": preset_none,
}
