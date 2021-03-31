from typing import Dict, List
import networkx as nx
from parchmint.component import Component
from parchmint.connection import Connection

from config import getFlowRate, getInletsAndOutlets, getPressure

from ufssanalyzer.electrical.constants import IN
from ufssanalyzer.electrical.cPoint import CPoint
from ufssanalyzer.electrical.rElement import RElement
from parchmint import Device


class ENetwork:
    def __init__(self, device: Device):
        self.G = nx.Graph()
        self.iocalculationPoints: Dict[str, CPoint] = dict()
        self.internalCalculationPoints: Dict[str, CPoint] = dict()
        self.flowRateIOComponents: List[Component] = []
        self.rElements = dict()
        self.componentCPoints = dict()

        self.inoutdata = getInletsAndOutlets()

        if device:
            print("Generating Electical Network from Microfluidic Network")
            self.generateFromDevice(device)
            print("Annotating the Electical Network from Config Data")
            self.annotate()
            # print(self.iocalculationPoints)

    def generateFromDevice(self, device: Device) -> None:
        self.device = device
        components = device.get_components()
        connections = device.get_connections()

        # Generate all the RElements which will eventually become the edges
        # Add components as nodes
        for component in components:
            if self.isInletOutlet(component):
                self.flowRateIOComponents.append(component)
            else:
                print("Creating R Element for component: ", component.name)
                relement = RElement.generateRElementFromComponent(component)
                self.rElements[relement.id] = relement

        # Add connections as nodes
        for connection in connections:
            relements = RElement.generateRElementsFromConnection(connection)

            # Add each of the relements from the static method
            for relement in relements:
                self.rElements[relement.id] = relement

        # Generate calculation points for all the inlets and outlets
        for component in self.flowRateIOComponents:
            cpoint = CPoint(component.ID)
            self.iocalculationPoints[cpoint.id] = cpoint
            self.G.add_node(cpoint.id, data=cpoint)

        # Loop through all the connections again to generate the ENetworkGraph
        # them as edges in the graph while making all the additional calculationpoints
        for connection in connections:
            self.addConnectionCalculationPoints(connection)

        # Now create all component based connections
        for component in components:
            if not self.isInletOutlet(component):
                self.connectComponentRElements(component)

    def getEdgeData(self, edge):
        data = self.G.get_edge_data(edge[0], edge[1])
        # TODO: Rectify how this implemented so tha we dont have the same issues
        return data["data"]

    def updateState(self, name, state):
        for vertex in self.G.nodes:
            if vertex == name:
                cpoint = self.getCPoint(name)
                # print("Found cpoint:.....", name, cpoint)
                if IN == state:
                    cpoint.flowrate = getFlowRate(name)
                else:
                    cpoint.pressure = getPressure(name)

    def isInletOutlet(self, component: Component) -> bool:
        print("inout data:", self.inoutdata)
        for key in self.inoutdata:
            if key == component.ID:
                return True

        return False

    def annotate(self) -> None:
        for key in self.inoutdata:
            print("Annotating Config entry: ", key)
            self.updateState(key, self.inoutdata[key])

    def connectComponentRElements(self, component: Component) -> None:
        # print("Component CPoints: ", self.componentCPoints[component.ID])
        cpoints = self.componentCPoints[component.ID]
        relement = self.rElements[component.ID]

        if len(cpoints) == 2:
            self.G.add_edge(cpoints[0].id, cpoints[1].id, data=relement)

        else:
            raise Exception("Cannot account for components greater than 2")

    def mapCPointForComponent(self, componentname: str, cpoint: CPoint) -> None:
        # print("mapCPointForComponent - component name: ", componentname)
        array = None
        if componentname in self.componentCPoints:
            array = self.componentCPoints[componentname]
        else:
            array = []

        array.append(cpoint)
        self.componentCPoints[componentname] = array
        # print("CPOINT MAP: ", self.componentCPoints.keys())

    def addConnectionCalculationPoints(self, connection: Connection) -> None:
        # Get the connection source and sink, if its a inlet outlet, get the corresponding CPoint
        source = connection.source
        sourceref = source.component
        source_cpoint = None
        cpoint_id = None

        for sink in connection.sinks:
            sinkref = sink.component
            sink_cpoint = None
            assert source is not None
            cpoint_id = CPoint.generateCPointNameFromTarget(source)

            if sourceref in self.iocalculationPoints:
                print("Found source ref as calculation point")
                source_cpoint = self.iocalculationPoints[sourceref]

            elif cpoint_id in self.internalCalculationPoints:
                source_cpoint = self.internalCalculationPoints[cpoint_id]

            else:
                print("Brand new source calculation point")
                source_cpoint = CPoint(cpoint_id)
                self.internalCalculationPoints[cpoint_id] = source_cpoint
                self.mapCPointForComponent(sourceref, source_cpoint)
                # Now add the CPoint Node to graph
                self.G.add_node(cpoint_id, data=source_cpoint)

            cpoint_id = CPoint.generateCPointNameFromTarget(sink)

            if sinkref in self.iocalculationPoints:
                print("Found sink as calculation point")
                sink_cpoint = self.iocalculationPoints[sinkref]

            elif cpoint_id in self.internalCalculationPoints:
                sink_cpoint = self.internalCalculationPoints[cpoint_id]

            else:
                print("Brand new sink calculation point")
                sink_cpoint = CPoint(cpoint_id)
                self.internalCalculationPoints[cpoint_id] = sink_cpoint
                self.mapCPointForComponent(sinkref, sink_cpoint)
                # Now add the CPoint Node to graph
                self.G.add_node(cpoint_id, data=sink_cpoint)

            # Get the Edge Data (RElement corresponding to (source, sink) pair)
            relement = self.rElements[
                RElement.getRElementNameForConnection(source, sink)
            ]
            # print("Queried RElement: ", relement)
            print("Creating Edge for: ", sourceref, sinkref)
            print("Creating Edge for: ", source_cpoint.id, sink_cpoint.id)

            self.G.add_edge(source_cpoint.id, sink_cpoint.id, data=relement)

    def getCPoint(self, cpoint_id: str) -> CPoint:
        return self.G.nodes[cpoint_id]["data"]

    def getResistanceBetween(self, source_id: str, sink_id: str) -> float:
        data = self.G.get_edge_data(source_id, sink_id)
        return data["data"].resistance

    def updatePressure(self, cpoint_id: str, value: float) -> None:
        cpoint = self.getCPoint(cpoint_id)
        cpoint.pressure = value

    def getAllCPoints(self) -> List[CPoint]:
        ret = [self.getCPoint(node) for node in self.G.nodes]
        return ret