import networkx as nx
from config import getFlowRate, getInletsAndOutlets, getPressure
from .rElement import RElement
from .cPoint import CPoint
from .constants import IN

class ENetwork:

    def __init__(self, device):
        self.G = nx.MultiGraph()
        self.calculationPoints = []

        if device:
            self.generateFromDevice(device)
            self.annotate()
            print(self.calculationPoints)
    
    def generateFromDevice(self, device):
        components = device.getComponents()
        connections = device.getConnections()

        #Add components as nodes
        for component in components:
            relement = RElement.generateRElementFromComponent(component)
            self.G.add_node(relement.id, data=relement)

        #Add connections as nodes
        for connection in connections:
            relement = RElement.generateRElementFromConnection(connection)
            self.G.add_node(relement.id, data=relement)

        #Loop through all the connections to add 
        # them as edges in the graph
        for connection in connections:
            self.addCalculationPoint(connection)


    def getEdgeData(self, edge):
        data = self.G.get_edge_data(edge[0], edge[1])
        return data[0]['data']


    def updateState(self, name, state):
        for vertex in self.G.nodes():
            if vertex == name:
                edges_to_modify = nx.edges(self.G, vertex)
                for edge in edges_to_modify:
                    cpoint = self.getEdgeData(edge)
                    cpoint.state = state

                    if IN == state:
                        cpoint.flowrate = getFlowRate(name)
                    else:
                        cpoint.pressure = getPressure(name)

    def annotate(self):
        inoutdata = getInletsAndOutlets()
        for key in inoutdata:
            # print(key, inoutdata[key])
            self.updateState(key, inoutdata[key])

    def addCalculationPoint(self, connection):

        sourceref = connection.source.component
        cpoint = CPoint()
        self.G.add_edge(connection.name, sourceref, data=cpoint)
        self.calculationPoints.append(cpoint)

        for sink in connection.sinks:
            sinkref = sink.component
            cpoint = CPoint()
            self.G.add_edge(connection.name, sinkref, data=cpoint)
            self.calculationPoints.append(cpoint)


    