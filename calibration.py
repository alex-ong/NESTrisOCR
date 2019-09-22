import configparser
from ast import literal_eval #safe version of eval

config = configparser.ConfigParser()
config.read('config.ini')

WINDOW_NAME = config['calibration']['window_name']
CAPTURE_COORDS = literal_eval(config['calibration']['game_coords'])
scorePerc = literal_eval(config['calibration']['scorePerc'])
linesPerc = literal_eval(config['calibration']['linesPerc'])
levelPerc = literal_eval(config['calibration']['levelPerc'])
statsPerc  = literal_eval(config['calibration']['statsPerc'])
stats2Perc = literal_eval(config['calibration']['stats2Perc'])
