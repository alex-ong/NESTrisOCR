import configparser
from ast import literal_eval #safe version of eval

class Configuration:
    def __init__(self, parser):
        self._parser = parser        
        #player
        self.player_name = parser['player']['name']
        self.twitch_url = parser['player']['twitch']
        #calibration
        self.WINDOW_NAME = parser['calibration']['window_name']
        self.CAPTURE_COORDS = literal_eval(parser['calibration']['game_coords'])
        self.scorePerc = literal_eval(parser['calibration']['scorePerc'])
        self.linesPerc = literal_eval(parser['calibration']['linesPerc'])
        self.levelPerc = literal_eval(parser['calibration']['levelPerc'])
        self.statsPerc  = literal_eval(parser['calibration']['statsPerc'])
        self.stats2Perc = literal_eval(parser['calibration']['stats2Perc'])
        

parser = configparser.ConfigParser()
parser.read('config.ini')

config = Configuration(parser)

