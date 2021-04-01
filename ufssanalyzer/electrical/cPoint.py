from typing import Optional
from parchmint.target import Target


class CPoint:
    """CPoint/Calculation point is the class that encapsulates the point of interest where
    flowequaitons are constructed and the states are evaluated.
    """

    def __init__(self, id: str, target: Optional[Target]):
        """Initializes a new CPoint

        Arguments:
            id {string} --
        """
        self.id = id
        self.pressure: Optional[float] = None
        self.flowrate: Optional[float] = None
        # TODO - Change this to enum associated with known pressure and known flowrate
        self.state: str = None
        self._target_ref: Optional[Target] = target

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def generate_CPoint_name_from_target(target: Target) -> str:
        """Generates the identifier that has follows the required cpoint convention

        Arguments:
            target {Target} -- Target corresponding to the connection

        Returns:
            [str] -- Name of the cpoint
        """
        target_port = target.port
        if target_port == None:
            target_port = ""
        return target.component + "_" + target_port
