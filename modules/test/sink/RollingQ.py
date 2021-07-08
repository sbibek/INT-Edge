class RollingQ:
    def __init__(self, size = 4):
        self.lastRolledValue = -1 
        self.data = []
        self.size = size

        self.bypass = True

    def push(self, datapoint):
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

