class CPoint:

    def __init__(self):
        self.pressure = None
        self.flowrate = None
        self.state = None


    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

