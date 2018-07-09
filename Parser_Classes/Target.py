class Target:

    def __init__(self,component,port):
        self.component = component
        self.port = port

    def __str__(self):
        return str(self.__dict__)
        