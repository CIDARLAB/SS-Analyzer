class Connection:
    """[Stores all connection information from JSON design file. Component information used to
    generate electrical model in multigraph structure]
    """

    def __init__(self,sinks,name,ID,source,params,layer):
        self.sinks = sinks
        self.name = name
        self.id = ID
        self.source = source
        self.params = params
        self.layer = layer 

    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)
