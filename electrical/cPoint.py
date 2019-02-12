class CPoint:
    """CPoint/Calculation point is the class that encapsulates the point of interest where
    flowequaitons are constructed and the states are evaluated

    Returns:
        [type] -- [description]
    """
    
    def __init__(self, id):
        """[summary]
        
        Arguments:
            id {string} -- 
        """
        self.id = id
        self.pressure = None
        self.flowrate = None
        self.state = None


    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)
    

    @staticmethod
    def generateCPointNameFromTarget(target):
        """Generates the identifier that has follows the required cpoint convention
        
        Arguments:
            target {Target} -- [description]
        
        Returns:
            [type] -- [description]
        """
        target_port = target.port
        if target_port == None:
            target_port = ""
        return target.component + "_" + target_port

