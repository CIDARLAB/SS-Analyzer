#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request
import sys
import argparse


from parser import parser


from solver import solver

# app = Flask(__name__)

# tasks = [
#     {
#         'id': 1,
#         'title': u'Buy groceries',
#         'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
#         'done': False
#     },
#     {
#         'id': 2,
#         'title': u'Learn Python',
#         'description': u'Need to find a good Python tutorial on the web', 
#         'done': False
#     }
# ]

argparser = argparse.ArgumentParser()

argparser.parse_args()


   
JSON = request.get_json()
G = parser.Parse(JSON)

edge_list = G.edges()

r_data = annotate(G,JSON)

edge_list = G.edges()

for edge in edge_list:
    current_edge = G.get_edge_data(edge[0],edge[1])
    print(edge) 
    print(current_edge)
    print("\n")

solver.solve(G,r_data)

for edge in edge_list:
    current_edge = G.get_edge_data(edge[0],edge[1])
    print(current_edge)
    print("\n")


jsonify(JSON)
