class Target:
    """[Stores all target information from JSON design file. Currently unused in multigraph.]
    """

    def __init__(self,component,port):
        self.component = component
        self.port = port

    def __str__(self):
        return str(self.__dict__)
        