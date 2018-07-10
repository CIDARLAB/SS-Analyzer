class Pressure:
    """[Contains id and pressure value for each terminal in multigraph. Will contain 
    calculated pressure drop value after calculations.]
    """

    def __init__(self,id,pressure):
        self.id = id
        self.p_val = pressure
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)