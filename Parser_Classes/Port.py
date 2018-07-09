class Port:

    def __init__(self,x,y,label,layer):
        self.x = x
        self.y = y
        self.label = label
        self.layer = layer

    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)
