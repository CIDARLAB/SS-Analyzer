from __future__ import annotations
from typing import List, Optional

from parchmint.component import Component
from parchmint.connection import Connection
from parchmint.target import Target
from ufssanalyzer.electrical.resistance import rModel as RModel


class RElement:
    def __init__(self, id: str, resistance: float):
        """Creates a new instance of the RElement with the given resistance


        Args:
            id (str): ID of the RElement
            resistance (float): Resistance value the REelement should take
        """
        self.id: str = id
        self._resistance: float = resistance
        self.state: Optional[str] = None

    @property
    def resistance(self) -> float:
        """Returns the fluidic resistance value of the RElement

        Returns:
            float: returns the resistance value
        """
        return self._resistance

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def generate_relement_from_component(component: Component) -> RElement:
        """Generate the RElement from the Component

        This uses our "little wizard of oz" function `compute_component_resistance`
        that is supposed tof figure out what the resistance is. This is currently
        only implemented for

        Args:
            component (Component): [description]

        Returns:
            RElement: [description]
        """
        R = RModel.compute_component_resistance(component)
        relement = RElement(component.ID, R)
        return relement

    @staticmethod
    def generate_relements_from_connection(connection: Connection) -> List[RElement]:
        """Generates relements_from_connection

        TODO - Be more sophisticated in generating the RElement and generate
        nodes for waypoints

        Args:
            connection (Connection): [description]

        Returns:
            List[RElement]: [description]
        """
        ret = []
        source = connection.source
        for sink in connection.sinks:
            print(connection.params.data)
            R = RModel.compute_connection_resistance(connection)
            print("resistance: ", R)
            assert source is not None
            relement = RElement(
                RElement.get_relement_name_for_connection(source, sink), R
            )
            ret.append(relement)
        return ret

    @staticmethod
    def get_relement_name_for_connection(source: Target, sink: Target) -> str:
        """Generates a name for the connection RElement based on the source and sink target

        #TODO - Write why this naming scheming is imporatant

        Args:
            source (Target): Source Target
            sink (Target): Sink Element

        Returns:
            str: name of the Relement
        """
        source_port = source.port
        sink_port = sink.port
        if source_port == None:
            source_port = ""
        if sink_port == None:
            sink_port = ""
        return (
            source.component
            + "_"
            + source_port
            + "_"
            + sink.component
            + "_"
            + sink_port
        )
