#!flask/bin/python

import sys
import argparse
import json
from parser import parser
from solver import solver
from config import parseConfig

argparser = argparse.ArgumentParser()
argparser.add_argument("design", help="JSON file to Analyze")
argparser.add_argument("-i","--input", help="Config file")

args = argparser.parse_args()

file_c = open(args.input, 'r')
parseConfig(file_c)

file_d = open(args.design, "r")
JSON = json.loads(file_d.read())
G = parser.Parse(JSON)

print(G)

edge_list = G.edges()

r_data = solver.annotate(G,JSON)

edge_list = G.edges()
print(edge_list)


print("Printing Annotated Data")
print("\n")

for edge in edge_list:
    current_edge = G.get_edge_data(edge[0],edge[1])
    print(edge) 
    print(current_edge)
    print("\n")

solver.solve(G,r_data)


print("Printing Solved Data")
print("\n")

for edge in edge_list:
    current_edge = G.get_edge_data(edge[0],edge[1])
    print(current_edge)
    print("\n")



