class CPoint:

    def __init__(self, id):
        self.id = id
        self.pressure = None
        self.flowrate = None
        self.state = None


    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)
    

    @staticmethod
    def generateCPointNameFromTarget(target):
        return target.component+"_"+target.port

