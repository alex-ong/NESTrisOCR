def lerp(start, end, perc):
    return perc * (end-start) + start
    
def mult_rect(rect, mult):
    return (round(rect[2]*mult[0]+rect[0]),
            round(rect[3]*mult[1]+rect[1]),
            round(rect[2]*mult[2]),
            round(rect[3]*mult[3]))


    
class ScoreFixer(object):
    def __init__(self, pattern):
        self.lastGoodValue = None
        self.pattern = pattern
        self.doFix = (pattern[0] == 'A')
        
    def fix(self,stringNumber):
        if not self.doFix:
            return stringNumber
            
        #quick hack to differentiate '8' and 'B' based on previous value
        if stringNumber is None or self.lastGoodValue is None:
            return stringNumber
            
        #switch first digit between 8 and B dependant on last state.    
        if self.lastGoodValue[0] == 'A' or self.lastGoodValue[0] == 'B':
            if stringNumber[0] == '8':
                stringNumber = 'B' + stringNumber[1:]
        
        if self.lastGoodValue[0] == '7' or self.lastGoodValue[0] == '8':
            if stringNumber[0] == 'B':
                stringNumber = '8' + stringNumber[1:]
        
        self.lastGoodValue = stringNumber
        
        return stringNumber