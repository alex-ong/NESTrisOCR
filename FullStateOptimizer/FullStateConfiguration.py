
import OCRHelpers



class FullStateConfiguration(object):
    def __init__(self, config):
        self.config = config
        self.capture_field = self.determine_capture_field(config)
        self.capture_stats = config.capture_stats
        self.capture_preview = config.capture_preview
        self.capture_flash = self.determine_capture_flash(config)        

    def determine_capture_field(self, config):
        if config.capture_field:
            return True
        elif config.flashMethod == 'FIELD':
            return True
        elif config.capture_stats and config.stats_method == 'FIELD':
            return True
    
    def determine_capture_flash(self, config):
        return config.flashMethod == 'FIELD' or config.flashMethod == 'BACKGROUND'
