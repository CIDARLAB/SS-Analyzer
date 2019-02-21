from math import *

#Initalize variables 
W_viscosity = 8.9*pow(10,-4)
#milli = pow(10,-3)
micro = pow(10,-6)

#include depth input after JSON fixed
def Channel_R(params):


    width = float(channelWidth)
    depth = float(depth)
    
    #HARD CODED VALUE OF LENGTH
    length = 2000.00

    width = width*micro
    depth = depth*micro
    length = length*micro

    alpha = 12*pow(1-((192*depth)/(pow(pi,5)*width))*tanh((pi*width)/(2*depth)),-1)
    resistance = (alpha*W_viscosity*length)/(width*pow(depth,3))

    return resistance

#print(Mixer_R(bendSpacing,numberOfBends,channelWidth,bendLength))