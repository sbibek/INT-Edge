class RollingQ:
    def __init__(self, size = 4):
        self.lastRolledValue = -1 
        self.data = []
        self.size = size

    def push(self, datapoint):
        self.data.append(datapoint)
        if len(self.data) == self.size:
            self.lastRolledValue = self.avg()
            self.data.pop(0)
        
    def avg(self):
        if len(self.data) < self.size:
            return -1
        return round(sum(self.data)/(self.size * 1.0),3)

