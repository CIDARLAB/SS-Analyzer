from math import *

#Initalize variables 
milli = pow(10,-3)
micro = pow(10,-6)
test = True

print("Hello this script is intended to measure the resistance of a tree")
width,depth = input("Insert channel width and depth (um): ").split()
length = input("Insert channel length (mm): ")
#leaf = input("Inset number of leafs: ")

#Reassign inputs as float 
width = float(width)
depth = float(depth)
length = float(length)
leaf = float(leaf)
width = width*micro
depth = depth*micro
length = length*milli

HD = width
#HD = (2*depth*width)/(depth+width)
#print("Hydraulic Diameter = ", HD)

sum_const = 1.875

resistance = ((2*pi*length)/(4*pow(HD,2)))*sum_const

print("resistance*C = ", resistance)
