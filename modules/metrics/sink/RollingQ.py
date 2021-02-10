import time
from conf import conf


class RollingQ:
    def __init__(self, size = 4):
        self.period = conf.getPeriod()
        self.lastupdated = None
        self.lastRolledValue = -1 
        self.data = []
        self.size = size

        self.bypass = True

    def push(self, datapoint):
        current = time.time()
        if self.lastupdated == None:
            self.lastupdated = current
        elif current - self.lastupdated < self.period:
            return
        
        self.lastupdated = current
        if self.bypass == True:
            self.lastRolledValue = datapoint
        else:
            self.data.append(datapoint)
            if len(self.data) == self.size:
                self.lastRolledValue = self.avg()
                self.data.pop(0)
        
        
    def avg(self):
        if self.bypass == True:
            return self.lastRolledValue
        else:
            if len(self.data) < self.size:
                return -1
            return round(sum(self.data)/(self.size * 1.0),3)

