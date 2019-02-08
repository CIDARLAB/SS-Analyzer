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
        target_port = target.port
        if target_port == None:
            target_port = ""
        return target.component + "_" + target_port

