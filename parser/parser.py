#Implementation of back end code 

from .component import Component
from .connection import Connection
from .port import Port
from .target import Target
import networkx as nx
import json

def Parse(JSON):    
    #Initialize Variables
    #parsed_JSON = json.load(open('JSON_Tests/test.json'))
    parsed_JSON = JSON
    G = nx.MultiGraph()
    components = []
    connections = []
    targets = []

    #Iterate through components and save as Component Objects
    for component in parsed_JSON["components"]:
        name = component["name"]
        layers = component["layers"]
        ID = component["id"]
        params = component["params"]
        ports = component["ports"]
        entity = component["entity"]
        num_ports = len(component["ports"])
        
        #Reset list of Port Objects 
        ports_to_add = []

        #For each component save port data as Port Object
        if(num_ports != 0):
            for port in ports:
                x = port["x"]
                y = port["y"]
                label = port["label"]
                layer = port["layer"]
                
                #Append list of Port Objects
                ports_to_add.append(Port(x,y,label,layer))

                #Append list of Target Objects 
                targets.append(Target(ID,Port(x,y,label,layer)))
        
        #Append list of Component Objects using list of Port Objects 
        components.append(Component(name,layers,ID,params,ports_to_add,entity))

    #Iterate through connections and save as Component Objects 
    for connection in parsed_JSON["connections"]:
        sinks = connection["sinks"]
        name = connection["name"]
        ID = connection["id"]
        source = connection["source"]
        params = connection["params"]
        layer = connection["layer"]

        #Append list of Connection Objects 
        connections.append(Connection(sinks,name,ID,source,params,layer))


    #For each component connect to channel and vice versa and include resistance values in graph 
    for component in parsed_JSON["components"]:
        for connection in parsed_JSON["connections"]:
            #Create edges from source to primitive 
            if(component["id"] == connection["source"]["component"]):
                #If Port is source flow rate is equal to the flow in
                if(component["entity"] == "PORT"):
                    G.add_edge(component["id"],connection["name"], Port = "Source", pressure = None, flow_eq = None, flow = None)
                #All other cases
                else:
                    G.add_edge(connection["name"],component["id"], Port = None, pressure = None, flow_eq = None, flow = None)
            #Create edges from primitive to sinks
            if(component["id"] == connection["sinks"][0]["component"]):
                #If Port is sink it is a final output and you can set the pressure to atm pressure (Pa)
                if(component["entity"] == "PORT"):
                    #101325 Pa is atmospheric pressure 
                    G.add_edge(connection["name"],component["id"], Port = "Sink", pressure = None, flow_eq = None, flow = None)
                #All other cases 
                else:
                    G.add_edge(connection["name"],component["id"], Port = None, pressure = None, flow_eq = None, flow = None)

    return G