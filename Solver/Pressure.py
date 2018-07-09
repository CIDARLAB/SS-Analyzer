class Pressure:

    def __init__(self,id,pressure):
        self.id = id
        self.p_val = pressure
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)