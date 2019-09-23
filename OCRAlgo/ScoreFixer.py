class ScoreFixer(object):
    def __init__(self, pattern):
        self.lastGoodValue = None
        self.pattern = pattern
        self.doFix = (pattern[0] == 'A')
        
    def fix(self,stringNumber):
        if not self.doFix:
            return stringNumber
            
        #quick hack to differentiate '8' and 'B' based on previous value
        if stringNumber is None:
            return stringNumber
        
        if self.lastGoodValue is None:
            self.lastGoodValue = stringNumber
            
        #switch first digit between 8 and B dependant on last state.    
        if self.lastGoodValue[0] == 'A' or self.lastGoodValue[0] == 'B':
            if stringNumber[0] == '8':
                stringNumber = 'B' + stringNumber[1:]
        
        if self.lastGoodValue[0] == '7' or self.lastGoodValue[0] == '8':
            if stringNumber[0] == 'B':
                stringNumber = '8' + stringNumber[1:]
        
        self.lastGoodValue = stringNumber
        
        return stringNumber