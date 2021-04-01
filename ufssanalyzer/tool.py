#!/usr/bin/python

import argparse
import json
import sys

from ufssanalyzer.config import parseConfig
from ufssanalyzer.electrical.eNetwork import ENetwork
from parchmint.device import Device
from ufssanalyzer.solver.solver import Solver


def solve_network():
    """CLI interface method for solver"""

    argparser = argparse.ArgumentParser()
    argparser.add_argument("design", help="JSON file to Analyze")
    argparser.add_argument("-i", "--input", help="Config file")

    args = argparser.parse_args()

    file_c = open(args.input, "r")
    file_d = open(args.design, "r")

    JSON = json.loads(file_d.read())

    device = Device(JSON)

    parseConfig(file_c, device)

    print("Printing the Micrfluidic Network's edges:")
    for edge in device.G.edges():
        print("Printing Edge :", edge)

    electrical_network = ENetwork(device)

    print("Printing the Electical Network's edges:")
    for edge in electrical_network.G.edges():
        print("Printing Edge :", edge, electrical_network.get_edge_data(edge))

    solver = Solver()
    solver.initialize(electrical_network)
    solver.solve()

    print("Final Results")
    for cpoint in electrical_network.getAllCPoints():
        parts = cpoint.id.split("_")
        nodename = device.get_component(parts[0]).name

        if len(parts) > 1:
            nodename = device.get_component(parts[0]).name + "_" + parts[1]

        print("Node: ", nodename, " Pressure: ", cpoint.pressure)


if __name__ == "__main__":
    # execute only if run as a script
    solve_network()