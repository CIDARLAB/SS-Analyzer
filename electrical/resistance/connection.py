from math import pow, sqrt, tanh, pi

from .constants import MICRONS, WATER_VISCOSITY

def pointDist(pointA, pointB):
    return sqrt(pow(pointA[0] - pointB[0], 2) + pow(pointA[1] - pointB[1], 2))


def connection_R(params):
    width = float(params["channelWidth"])
    depth = float(params["height"])
    length = 0
    for segment in params['segments']:
        pointA = segment[0]
        pointB = segment[1]

        length = length + pointDist(pointA, pointB)
    
    width = width * MICRONS
    depth = depth * MICRONS
    length = length * MICRONS

    alpha = 12*pow(1-((192*depth)/(pow(pi,5)*width))*tanh((pi*width)/(2*depth)),-1)
    resistance = (alpha*WATER_VISCOSITY*length)/(width*pow(depth,3))

    return resistance

def Dimension_Adjustment(length,bendSpacing,numberOfBends,bendLength,Calc_length):
    
    #Intialize Variables
    micro = pow(10,-6)
    #Given that length is proportional to delta_P tolerance is in range of 10^-5
    tolerance = .0001

    #Base Case Which Previous Calculated R Value Matches Desired R Difference within Specified Tolerance 
    if(Calc_length > length - tolerance and Calc_length < length + tolerance):
        print("Calc_length = %f" % Calc_length)
        mixer_dim = {
            "bendSpacing": bendSpacing,
            "numberOfBends": numberOfBends,
            "bendLength": bendLength,
        }
        return mixer_dim
    else:
        #Accounting for Initial Input
        if numberOfBends == 0 and bendLength == 0:
            #Set Variables Equal to Default Values (from 3duF)
            numberOfBends = 1.
            bendLength = 2460. * micro

            #Calculate Length Using New Set of Input Paramters
            test_length = numberOfBends * ((2*bendLength) + (2*bendSpacing))
            print("test_length = %f" % test_length)
            
            #Cases
            if(test_length > length - tolerance and test_length < length + tolerance):
                return Dimension_Adjustment(length,bendSpacing,numberOfBends,bendLength,test_length)
            ##################################################################################################
            elif(test_length < 0.0):
                print("Error")
                print("bendSpacing = %f" % bendSpacing)
                print("bendLength = %f" % bendLength)
                print("numberofBends = %f" % numberOfBends)
                return None
            ##################################################################################################
            elif(test_length < length):
                return Dimension_Adjustment(length,bendSpacing,numberOfBends + 1,bendLength + (150*micro),test_length)
            elif(test_length > length):
                bendLength_2 = ((length/numberOfBends) - (2*bendSpacing))/2.
                test_length = numberOfBends * ((2*bendLength_2) + (2*bendSpacing))
                print("EQUATION TO SOLVE FOR BENDLENGTH")
                print("bendLength = %f" % bendLength_2)
                print("numberOfBends = %i" % numberOfBends)
                print("test_length = %f" % test_length)
                print("length = %f" % length) 
            
        else:
            #Calculate Length Using New Set of Input Paramters
            test_length = numberOfBends * ((2*bendLength) + (2*bendSpacing))
            print("test_length = %f" % test_length)
            
            #Cases
            if(test_length > length - tolerance and test_length < length + tolerance):
                return Dimension_Adjustment(length,bendSpacing,numberOfBends,bendLength,test_length)
            ##################################################################################################
            elif(test_length < 0):
                print("Error")
                print("bendSpacing = %f" % bendSpacing)
                print("bendLength = %f" % bendLength)
                print("numberofBends = %f" % numberOfBends)
                return None
            ##################################################################################################
            elif(test_length < length):
                bendLength_2 = ((length/numberOfBends) - (2*bendSpacing))/2.
                test_length = numberOfBends * ((2*bendLength_2) + (2*bendSpacing))
                print("\n")
                print("##################################################################################################")
                print("numberOfBends = %i" % numberOfBends)
                print("bendLength = %f" % bendLength_2)
                print("test_length = %f" % test_length)
                print("length = %f" % length) 
                print("##################################################################################################")
                print("\n")
                return Dimension_Adjustment(length,bendSpacing,numberOfBends + 1,bendLength + (150*micro),test_length)
            elif(test_length > length):
                bendLength_2 = ((length/numberOfBends) - (2*bendSpacing))/2.
                test_length = numberOfBends * ((2*bendLength_2) + (2*bendSpacing))
                print("EQUATION TO SOLVE FOR BENDLENGTH")
                print("numberOfBends = %i" % numberOfBends)
                print("bendLength = %f" % bendLength_2)
                print("test_length = %f" % test_length)
                print("length = %f" % length) 



def Channel_Mod(R_Val,C_Width,C_Depth,Desired_R):

    #Initalize Variables
    W_viscosity = 8.9*pow(10,-4)
    micro = pow(10,-6)

    #Basic Error Check for Input Error or
    #Current Resistance is larger than Desired Resistance
    if(R_Val == Desired_R or R_Val > Desired_R):
        return None
    else:
        #Calculate Difference in R Values 
        R_Diff = Desired_R - R_Val
        #print("R_Diff = %f" % R_Diff)
        #Set Constant Values for depth and width according to original channel input 
        depth = C_Depth * micro
        width = C_Width * micro
        bendSpacing = 2 * width

        #Dimensionless constant used to calculate resistance 
        alpha = 12*pow(1-((192*depth)/(pow(pi,5)*width))*tanh((pi*width)/(2*depth)),-1)
        #print("alpha = %f" % alpha)

        #Total Length of Mixer Needed To Match Desired R
        length = (R_Diff*(width*pow(depth,3)))/(alpha*W_viscosity)
        print("Length = %f" % length)

        params = Dimension_Adjustment(length,bendSpacing,0,0,0)
        print(params)



    
    