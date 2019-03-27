#!/usr/bin/python

import argparse
import json
import sys

from config import parseConfig
from electrical.eNetwork import ENetwork
from pyparchmint.device import Device
from solver.solver import Solver

argparser = argparse.ArgumentParser()
argparser.add_argument("design", help="JSON file to Analyze")
argparser.add_argument("-i","--input", help="Config file")

args = argparser.parse_args()

file_c = open(args.input, 'r')
file_d = open(args.design, 'r')

JSON = json.loads(file_d.read())

device = Device(JSON)

parseConfig(file_c, device)

print("Printing the Micrfluidic Network's edges:")
for edge in device.G.edges():  
    print("Printing Edge :", edge)

electrical_network = ENetwork(device)

print("Printing the Electical Network's edges:")
for edge in electrical_network.G.edges():  
    print("Printing Edge :", edge, electrical_network.getEdgeData(edge))


solver = Solver()
solver.initialize(electrical_network)
solver.solve()

print("Final Results")
for cpoint in electrical_network.getAllCPoints():
    parts = cpoint.id.split("_")
    nodename = device.getNameForID(parts[0])

    if len(parts) > 1:
        nodename = device.getNameForID(parts[0]) + "_" + parts[1]
        
    print("Node: ", nodename, " Pressure: ", cpoint.pressure)



