import configparser
from configupdater import ConfigUpdater
from ast import literal_eval #safe version of eval

class Configuration:
    def __init__(self, filename, updater):
        self._filename = filename
        self._updater = updater
        self.initFromParser()
        
    def initFromParser(self):
        parser = configparser.ConfigParser()
        parser.read(self._filename)
        #player
        self.player_name = parser['player']['name']
        self.twitch_url = parser['player']['twitch']        
        #performance        
        self.threads = literal_eval(parser['performance']['multi_thread'])
        self.hexSupport = parser['performance'].getboolean('support_hex_score') 
        #stats
        self.capture_stats = parser['stats'].getboolean('read_stats')
        self.stats_method = parser['stats']['stats_method'].upper()
        #calibration
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
    
    def refresh(self):
        self._updater.update_file()
        self.initFromParser()
    
    def setItem(self,section,var,value):
        self._updater[section][var] = value
        self.refresh()
        
    def setPlayerName(self, name):
        self.setItem('player','name', name)
    
    def setTwitchURL(self, url):
        self.setItem('player','twitch', url)    
    
    def setThreads(self, threads):
        self.setItem('performance','multi_thread', threads)    
    
    def setHexSupport(self, support):
        self.setItem('performance','support_hex_score', support)    
    
    def setCaptureStats(self, toCapture):
        self.setItem('stats','read_stats', toCapture)    
    
    def setStatsMethod(self, val):
        self.setItem('stats','stats_method', val)    
    
    def setWindowName(self, val):
        self.setItem('calibration','window_name', val)    
    
    def setGameCoords(self, val):
        self.setItem('calibration','game_coords', val)    
        
    def setScorePerc(self, val):
        self.setItem('calibration','scorePerc', val)    
        
    def setLinesPerc(self, val):
        self.setItem('calibration','linesPerc', val)    
    
    def setLevelPerc(self, val):
        self.setItem('calibration','levelPerc', val)    
    
    def setStatsPerc(self, val):
        self.setItem('calibration','statsPerc', val)    
    
    def setStats2Perc(self, val):
        self.setItem('calibration','stats2Perc', val)    
    
    def setHost(self, val):
        self.setItem('network','host', val)    
    
    def setPort(self, val):
        self.setItem('network','port', val)    
    
updater = ConfigUpdater()        
updater.read('config.ini')

config = Configuration('config.ini', updater)


