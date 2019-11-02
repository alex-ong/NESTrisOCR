class ScoreFixer(object):
    def __init__(self, pattern):
        self.lastGoodValue = None
        self.pattern = pattern
        self.doFix = (pattern[0] == 'A')

    def charToDigit(self, item):
        if item in '0123456789':
            item = int(item)
        else:
            item = ord(item) - ord('A') + 10
        return item
        
    def digitToChar(self, item):
        if item < 10:
            item = str(item)
        else:
            item = chr(ord('A') + (item-10))
        return item
        
    def fix(self,stringNumber):
        if not self.doFix:
            return stringNumber
            
        #quick hack to differentiate '8' and 'B' based on previous value
        if stringNumber is None:
            return stringNumber
        
        if self.lastGoodValue is None:
            self.lastGoodValue = stringNumber
            
        goodFirstDigit = self.charToDigit(self.lastGoodValue[0])
        newFirstDigit = self.charToDigit(stringNumber[0])
        
        #we should only be able to up by one digit at a time...
        if newFirstDigit != goodFirstDigit and newFirstDigit != goodFirstDigit + 1:
            stringNumber = self.digitToChar(goodFirstDigit) + stringNumber[1:]
            
        #switch first digit between 8 and B dependant on last state.    
        if self.lastGoodValue[0] == 'A' or self.lastGoodValue[0] == 'B':
            if stringNumber[0] == '8':
                stringNumber = 'B' + stringNumber[1:]
        
        if self.lastGoodValue[0] == '7' or self.lastGoodValue[0] == '8':
            if stringNumber[0] == 'B':
                stringNumber = '8' + stringNumber[1:]
        
        #switch first digit between 4 and A dependant on last state.
        if self.lastGoodValue[0] == '9' or self.lastGoodValue[0] == 'A':
            if stringNumber[0] == '4':
                stringNumber = 'A' + stringNumber[1:]
        
        if self.lastGoodValue[0] == '3' or self.lastGoodValue[0] == '4':
            if stringNumber[0] == 'A':
                stringNumber = '4' + stringNumber[1:]
        self.lastGoodValue = stringNumber
        
        return stringNumber