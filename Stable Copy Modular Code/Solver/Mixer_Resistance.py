from math import *

#Initalize variables 
W_viscosity = 8.9*pow(10,-4)
#milli = pow(10,-3)
micro = pow(10,-6)

'''
bendSpacing = input("Insert bendSpacing: ")
numberOfBends = input("Insert numberofBends: ")
channelWidth = input("Insert channelWidth: ")
bendLength = input("Insert bendLength: ")
'''

#include depth input after JSON fixed
def Mixer_R(bendSpacing,numberOfBends,channelWidth,bendLength):

    
    #Reassign inputs as floats

    numberOfBends = float(numberOfBends)
    bendLength = float(bendLength)
    bendSpacing = float(bendSpacing)

    width = float(channelWidth)
    #depth = float(depth)
    #HARD CODED VALUE OF DEPTH
    depth = 400.00

    length = numberOfBends * ((2*bendLength) + (2*bendSpacing))

    width = width*micro
    depth = depth*micro
    length = length*micro

    alpha = 12*pow(1-((192*depth)/(pow(pi,5)*width))*tanh((pi*width)/(2*depth)),-1)
    resistance = (alpha*W_viscosity*length)/(width*pow(depth,3))

    return resistance

#print(Mixer_R(bendSpacing,numberOfBends,channelWidth,bendLength))