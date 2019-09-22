import configparser
from ast import literal_eval #safe version of eval

class Configuration:
    def __init__(self, parser):
        self._parser = parser        
        #player
        self.player_name = parser['player']['name']
        self.twitch_url = parser['player']['twitch']
        #performance        
        self.threads = literal_eval(parser['performance']['multi_thread'])
        self.hexSupport = parser['performance'].getboolean('support_hex_score')
        #calibration
        self.calibrate = parser['calibration'].getboolean('calibration_mode')
        self.WINDOW_NAME = parser['calibration']['window_name']
        self.CAPTURE_COORDS = literal_eval(parser['calibration']['game_coords'])
        self.scorePerc = literal_eval(parser['calibration']['scorePerc'])
        self.linesPerc = literal_eval(parser['calibration']['linesPerc'])
        self.levelPerc = literal_eval(parser['calibration']['levelPerc'])
        self.statsPerc  = literal_eval(parser['calibration']['statsPerc'])
        self.stats2Perc = literal_eval(parser['calibration']['stats2Perc'])
        #network
        self.host = parser['network']['host']
        self.port = literal_eval(parser['network']['port'])

parser = configparser.ConfigParser(allow_no_value=True)
parser.read('config.ini')

config = Configuration(parser)


