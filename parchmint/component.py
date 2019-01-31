from .params import Params

class Component:

    def __init__(self, json):
        self.name = None
        self.ID = None
        self.params = dict()

        if json:
            self.parseFromJSON(json)


    
    def parseFromJSON(self, json):
        self.name = json["name"]
        self.ID = json["id"]

        self.params = Params(json["params"])

    def __str__(self):
            return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)