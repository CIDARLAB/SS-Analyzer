from typing import Dict, List, Tuple
import networkx as nx
from parchmint.component import Component
from parchmint.connection import Connection
from parchmint.target import Target

from ufssanalyzer.config import get_flow_rate, get_inlets_outlets, get_pressure

from ufssanalyzer.electrical.constants import IN
from ufssanalyzer.electrical.cPoint import CPoint
from ufssanalyzer.electrical.rElement import RElement
from parchmint import Device


class ENetwork:
    def __init__(self, device: Device):
        self.G = nx.Graph()

        # TODO - Figure out how much the io vs internal calcuation points
        # is preventing us for calculating internal uknowns

        # Calculation points associated with the input / output components
        # (Since they're typically just one of them)
        self.io_calculation_points: Dict[str, CPoint] = dict()

        # Calculation points associated with the rest of the network
        self.internal_calculation_points: Dict[str, CPoint] = dict()
        self.flowRateIOComponents: List[Component] = []
        self.rElements = dict()
        self.component_CPoints = dict()

        self.inoutdata = get_inlets_outlets()

        if device:
            print("Generating Electical Network from Microfluidic Network")
            self.generate_from_device(device)
            print("Annotating the Electical Network from Config Data")
            self.__annotate()
            # print(self.iocalculationPoints)

    def generate_from_device(self, device: Device) -> None:
        """Generates the ENetwork from the given device and enables the representation
        of the design as an electrical network model.

        1. Goes through all the components and creates the RElements
        2. Goes through all the connections and creates the RElements
        3. Generates Calculation Points for all the inlets and outlets
        4. Loop through the connects at each location where a connection connects to a component
        5. Makes connections between the RElement in a single component

        Args:
            device (Device): The device from which we generate the electrical network
        """
        self.device = device
        components = device.get_components()
        connections = device.get_connections()

        # Generate all the RElements which will eventually become the edges
        # Add components as nodes
        for component in components:
            if self.is_inlet_outlet(component):
                self.flowRateIOComponents.append(component)
            else:
                print("Creating R Element for component: ", component.name)
                relement = RElement.generate_relement_from_component(component)
                self.rElements[relement.id] = relement

        # Generate all the rlements for the connections
        for connection in connections:
            relements = RElement.generateRElementsFromConnection(connection)

            # Add each of the relements from the static method
            for relement in relements:
                self.rElements[relement.id] = relement

        # Generate calculation points for all the inlets and outlets
        for component in self.flowRateIOComponents:
            # TODO - Remove the assumption that IO components only have 1,
            # Also figure out how to genrate targets here
            cpoint = CPoint(component.ID, None)
            self.io_calculation_points[cpoint.id] = cpoint
            self.G.add_node(cpoint.id, data=cpoint)

        # Loop through all the connections again to generate the ENetworkGraph
        # them as edges in the graph while making all the additional calculationpoints
        for connection in connections:
            self._add_connection_calculation_points(connection)

        # Now connect all Relements of individual components
        for component in components:
            if not self.is_inlet_outlet(component):
                self.connect_component_relements(component)

    def get_edge_data(self, edge: Tuple[str, str]):
        """Get data stored on the edge dictionary


        Args:
            edge (Tuple[str, str]): ENetwork edge we want to get the data for

        Returns:
            [type]: TBA
        """
        data = self.G.get_edge_data(edge[0], edge[1])
        # TODO: Rectify how this implemented so tha we dont have the same issues
        return data["data"]

    def update_state(self, id: str, state: str):
        """Updates the state of the ENetowkr node

        Args:
            id (str): id of the CPoint
            state (str): state we want to set for the CPoint
        """
        # TODO - Why am I looping through this, can we remove it and how do I ensure
        # that this is only meant for IO components
        for vertex in self.G.nodes:
            if vertex == id:
                cpoint = self.get_cpoint(id)
                # print("Found cpoint:.....", name, cpoint)
                if IN == state:
                    cpoint.flowrate = get_flow_rate(id)
                else:
                    cpoint.pressure = get_pressure(id)

    def is_inlet_outlet(self, component: Component) -> bool:
        """Checks if the given component is an input/ouput in the microfluidic device

        We do this by checking against the inoutdata dictionary that we load during the
        creating of the ENetwork creation

        Args:
            component (Component): Component that we want to check

        Returns:
            bool: True if component is an inlet / outlet component
        """
        print("inout data:", self.inoutdata)
        for key in self.inoutdata:
            if key == component.ID:
                return True

        return False

    def __annotate(self) -> None:
        """Annotates the components based on the initial config informatino

        This is used to set the initial information (known state values) in the ENetwork
        """
        for key in self.inoutdata:
            print("Annotating Config entry: ", key)
            self.update_state(key, self.inoutdata[key])

    def connect_component_relements(self, component: Component) -> None:
        """Connect the RElemnt in the ENetwork for the given component.

        This is necessary because we of the way we decompose the component into
        discrete RElements that we can then stitch together.

        TODO - Currently we are assuming there are only two elements connecting
        to each other, we need to figure out generalized ways to map how the components
        that are not 1->1 need to be stitched together.

        Args:
            component (Component): Component for we which we need to assemble a RElement Network

        Raises:
            Exception: When components with greater than 2 ports (Target objects) are encountered
        """

        # print("Component CPoints: ", self.componentCPoints[component.ID])
        cpoints = self.component_CPoints[component.ID]

        # TODO - make this work for the tuple of component ID and target
        relement = self.rElements[component.ID]

        if len(cpoints) == 2:
            self.G.add_edge(cpoints[0].id, cpoints[1].id, data=relement)

        else:
            raise Exception("Cannot account for components greater than 2")

    def map_cpoint_for_component(self, componentname: str, cpoint: CPoint) -> None:
        """Maps an association for a CPoint against an internal reverse look up
        dictionary to simplify life.

        Args:
            componentname (str): Component name against which we want to save the CPoint association
            cpoint (CPoint): CPoint we want to associate against the component
        """
        # print("mapCPointForComponent - component name: ", componentname)
        array = None
        if componentname in self.component_CPoints:
            array = self.component_CPoints[componentname]
        else:
            array = []

        array.append(cpoint)
        self.component_CPoints[componentname] = array
        # print("CPOINT MAP: ", self.componentCPoints.keys())

    def _add_connection_calculation_points(self, connection: Connection) -> None:
        """Adds the calculation points assoicated with a connection into the ENetwork

        Goes through each of the source sink pairs and then generate the caclulation points for each of them

        Args:
            connection (Connection): [description]
        """
        # Get the connection source and sink, if its a inlet outlet, get the corresponding CPoint
        source = connection.source
        sourceref = source.component
        source_cpoint = None
        cpoint_id = None

        for sink in connection.sinks:
            sinkref = sink.component
            sink_cpoint = None
            assert source is not None
            cpoint_id = CPoint.generate_CPoint_name_from_target(source)

            if sourceref in self.io_calculation_points:
                print("Found source ref as calculation point")
                source_cpoint = self.io_calculation_points[sourceref]

            elif cpoint_id in self.internal_calculation_points:
                source_cpoint = self.internal_calculation_points[cpoint_id]

            else:
                print("Brand new source calculation point")
                source_cpoint = CPoint(cpoint_id, source)
                self.internal_calculation_points[cpoint_id] = source_cpoint
                self.map_cpoint_for_component(sourceref, source_cpoint)
                # Now add the CPoint Node to graph
                self.G.add_node(cpoint_id, data=source_cpoint)

            cpoint_id = CPoint.generate_CPoint_name_from_target(sink)

            if sinkref in self.io_calculation_points:
                print("Found sink as calculation point")
                sink_cpoint = self.io_calculation_points[sinkref]

            elif cpoint_id in self.internal_calculation_points:
                sink_cpoint = self.internal_calculation_points[cpoint_id]

            else:
                print("Brand new sink calculation point")
                sink_cpoint = CPoint(cpoint_id, sink)
                self.internal_calculation_points[cpoint_id] = sink_cpoint
                self.map_cpoint_for_component(sinkref, sink_cpoint)
                # Now add the CPoint Node to graph
                self.G.add_node(cpoint_id, data=sink_cpoint)

            # Get the Edge Data (RElement corresponding to (source, sink) pair)
            relement = self.rElements[
                RElement.get_relement_name_for_connection(source, sink)
            ]
            # print("Queried RElement: ", relement)
            print("Creating Edge for: ", sourceref, sinkref)
            print("Creating Edge for: ", source_cpoint.id, sink_cpoint.id)

            self.G.add_edge(source_cpoint.id, sink_cpoint.id, data=relement)

    def get_cpoint(self, cpoint_id: str) -> CPoint:
        """Returns the cPoint assoicated with the ID in the network

        Args:
            cpoint_id (str): cpoint id

        Returns:
            CPoint: CPoint associated with the id
        """
        return self.G.nodes[cpoint_id]["data"]

    def get_resistance_between(self, source_cpoint_id: str, sink_sink_id: str) -> float:
        """Gets the resistance between 2 CPoints

        Args:
            source_cpoint_id (str): Source CPoint node
            sink_sink_id (str): Sink CPoint node

        Returns:
            float: Value of the Fluidic Resistance
        """
        data = self.G.get_edge_data(source_cpoint_id, sink_sink_id)
        return data["data"].resistance

    def update_pressure(self, cpoint_id: str, value: float) -> None:
        """Updates the pressure of the

        [extended_summary]

        Args:
            cpoint_id (str): [description]
            value (float): [description]
        """
        cpoint = self.get_cpoint(cpoint_id)
        cpoint.pressure = value

    def getAllCPoints(self) -> List[CPoint]:
        ret = [self.get_cpoint(node) for node in self.G.nodes]
        return ret