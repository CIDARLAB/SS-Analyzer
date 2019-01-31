class RElement:

    def __init__(self, id, resistance):
        self.id = id
        self.resistance = resistance
        self.state = None


    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def generateRElementFromComponent(component):
            relement = RElement(component.name, 100)
            return relement

    @staticmethod
    def generateRElementFromConnection(connection):
        relement = RElement(connection.name, 100)
        return relement
