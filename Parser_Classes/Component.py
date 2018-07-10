class Component:
    """[Stores all component information from JSON design file. Component information used to
    generate electrical model in multigraph structure]
    """


    def __init__(self,name,layers,ID,params,ports,entity):
        self.name = name
        self.layers = layers
        self.id = ID
        self.params = params
        self.ports = ports
        self.entity = entity

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)