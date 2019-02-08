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
    def generateRElementsFromConnection(connection):
        ret = []
        source = connection.source
        for sink in connection.sinks:
            relement = RElement(RElement.getRElementNameForConnection(source, sink), 100)
            ret.append(relement)
        return ret

    @staticmethod
    def getRElementNameForConnection(source, sink):
        source_port = source.port
        sink_port = sink.port
        if source_port == None:
            source_port = ""
        if sink_port == None:
            sink_port = ""
        return source.component + "_" + source_port + "_" + sink.component + "_" + sink_port


