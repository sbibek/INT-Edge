class RollingQ:
    def __init__(self, size = 4):
        self.data = []
        self.size = size

    def push(self, datapoint):
        if len(self.data) > self.size:
            self.data.pop(0)
        self.data.append(datapoint)
        
    def avg(self):
        if len(self.data) < self.size:
            return -1
        return round(sum(self.data)/(self.size * 1.0),3)

