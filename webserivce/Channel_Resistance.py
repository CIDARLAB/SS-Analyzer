from math import *

#Initalize variables 
W_viscosity = 8.9*pow(10,-4)
#milli = pow(10,-3)
micro = pow(10,-6)
test = True

#width = input("Insert width: ")
#depth = input("Insert depth: ")

#include length input after JSON is fixed 
def Channel_R(width, depth):

    #Reassign inputs as float 
    width = float(width)
    depth = float(depth)
    #length = float(length)
    length = 2000.00
    width = width*micro
    depth = depth*micro
    length = length*micro

    alpha = 12*(1*pow(1-((192*depth)/(pow(pi,5)*width))*tanh((pi*width)/(2*depth)),-1))
    resistance = (alpha*W_viscosity*length)/(width*pow(depth,3))

    return resistance

#print(Channel_R(width,depth))