from __future__ import annotations
from typing import List, Optional

from parchmint.component import Component
from parchmint.connection import Connection
from parchmint.target import Target
from ufssanalyzer.electrical.resistance import rModel as RModel


class RElement:
    def __init__(self, id: str, resistance: float):
        self.id: str = id
        self.resistance: float = resistance
        self.state: Optional[str] = None

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def generateRElementFromComponent(component: Component) -> RElement:
        R = RModel.computeComponentResistance(component)
        relement = RElement(component.ID, R)
        return relement

    @staticmethod
    def generateRElementsFromConnection(connection: Connection) -> List[RElement]:
        ret = []
        source = connection.source
        for sink in connection.sinks:
            print(connection.params.data)
            R = RModel.computeConnectionResistance(connection)
            print("resistance: ", R)
            assert source is not None
            relement = RElement(RElement.getRElementNameForConnection(source, sink), R)
            ret.append(relement)
        return ret

    @staticmethod
    def getRElementNameForConnection(source: Target, sink: Target) -> str:
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
