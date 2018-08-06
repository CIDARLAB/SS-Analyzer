import Mixer_Resistance
import Channel_Resistance
from __init__ import Pressure
import networkx as nx
import numpy as np
import json

def annotate(multinet,JSON):
    """[Calculate all resistance values using primitive resistance models and store in dictionary. Also
    annotate multigraph edges with pressure object and flow rate information]
    
    Arguments:
        multinet {Networkx Multigraph} -- Multigraph containing all component vertices with corresponding edges 
        (no additional information is annotated)

        JSON {JSON} -- 3duF/Fluigi produced JSON design file

    Returns:
        Resistance Dictionary {resistance_data} -- Dictionary containing all component or channel segments resistance values. 
        Key values are component id. 
    """


    #Include flow_dict in input arguments later to account for user specified flow rates 
    parsed_JSON = JSON
    G = multinet
    resistance_data = {}
    primitive_res = 0
    #Create edge_list object
    edge_list = G.edges()

    #Calculate all primitive resistances in JSON and create objects
    for component in parsed_JSON["components"]:

        if(component["entity"] == "MIXER"):
            bendSpacing = component["params"]["bendSpacing"]
            numberOfBends = component["params"]["numBends"]
            channelWidth = component["params"]["channelWidth"]
            bendLength = component["params"]["bendLength"]

            primitive_res = Mixer_Resistance.Mixer_R(bendSpacing,numberOfBends,channelWidth,bendLength)

            resistance_data[component["id"]] = primitive_res
        
        if(component["entity"] == "PORT"):

            primitive_res = 100
            resistance_data[component["id"]] = primitive_res

        #Calculate each channel connected to the primitive 
        for connection in parsed_JSON["connections"]:
            width = connection["params"]["width"]
            depth = connection["params"]["depth"]
            primitive_res = Channel_Resistance.Channel_R(width,depth)
            resistance_data[connection["id"]] = primitive_res
    
    #Use Flow Dictionary to input flow rate data accordingly 
    
    for edge in edge_list:
        current_edge_data = G.get_edge_data(edge[0],edge[1])
        #If current edge has a port for the sink then set the pressure equal to atm value
        if current_edge_data[0]["Port"] == "Sink":
            current_edge_data[0]["pressure"] = Pressure(edge[1],101325)
            current_edge_data[0]["flow"] = 0.
        #If port is not a sink then check other cases
        else:
            #If current edge has a port that is a source then set the flow rate equal to input flow rate
            if current_edge_data[0]["Port"] == "Source":
                current_edge_data[0]["pressure"] = Pressure(edge[0],None)
                current_edge_data[0]["flow"] = 1.
            #If current edge doesn't have a port for a sink or source then all values are unknown 
            elif current_edge_data[0]["Port"] == None :
                current_edge_data[0]["pressure"] = Pressure(edge[0],None)
                current_edge_data[0]["flow"] = 0.
    return resistance_data
        




def solve(multinet,r_data):
    """[Calculate pressure drop for each terminal (point where connenction meets component) in multigraph, and
    annotate edges for input Multigraph]
    
    Arguments:
        multinet {Networkx Multigraph} -- Multigraph containing all component vertices with corresponding edges. 
        Pressure objects and flow rates are annotated in Multigraph edges. 

        r_data {Dictionary} -- Dictionary containing all component or channel segments resistance values. 
        Key values are component id. 
    
    Returns:
        Networkx Multigraph {G} -- Multigraph containing all component vertices with corresponding edges. 
        Pressure drop values are appended to corresponding edges.  
    """


    G = multinet
    resistance_data = r_data
    #Create edge_list object
    edge_list = G.edges()

    #Initialize dict which stores how many outputs each primitive has
    multi_outputs = {}
    multi_inputs = {}

    #Establish how many primitives have multiple outputs to divide flow rate 
    for edge in edge_list:

        #Store key as source id and save with 1 output 
        if(edge[0] not in multi_outputs):
            multi_outputs[edge[0]] = 1
        #If key is already in dict then it means it is another source and will have another output
        elif(edge[0] in multi_outputs):
            multi_outputs[edge[0]] = multi_outputs[edge[0]] + 1
        
        #Store key as sink id and save with 1 input
        if(edge[1] not in multi_inputs):
            multi_inputs[edge[1]] = 1
        #If key is already in dict that means it is another sink and will have another input
        elif(edge[1] in multi_inputs):
            multi_inputs[edge[1]] = multi_inputs[edge[1]] + 1
    

    print("\n")
    print("MULTI OUTPUTS: ")
    print(multi_outputs)
    print("\n")
    print("MULTI INPUTS: ")
    print(multi_inputs)
    print("\n")

    #EXPERIMENTAL STUFF
    ##############################################################################################################

    '''
    for edge in edge_list:
        if multi_outputs[edge[0]] > 1:
            G.node[edge[0]]["Junction"] = True
    
    check_edge = []
    for edge in edge_list:
        if G.node[edge[0]]["Junction"] == True and edge[0] not in check_edge:
            check_edge.append(edge[0])
            for path in nx.all_simple_paths(G, source=edge[0], target="port_out"):
                #print(path)
                G.node[edge[0]]["R_Paths"][path[1]] = path
    
    #DOESN'T ACCOUNT FOR OTHER JUNCTIONS DOWNSTREAM
    for edge in edge_list:
        R_Sum = 0
        for path in G.node[edge[0]]["R_Paths"]:
            #Path is equal to key of path stored under R_Paths
            path_R = 0
            for comp in G.node[edge[0]]["R_Paths"][path]:
                if(comp != "port_out"):
                    if comp == G.node[edge[0]]["R_Paths"][path][0]:
                        path_R = path_R
                    elif G.node[comp]["Junction"] == True:
                        path_R = path_R + G.node[comp]["Total_R"]
                    else:
                        path_R = path_R + resistance_data[comp]
            #Set Path Resistance
            G.node[edge[0]]["R_Paths_Value"][path] = path_R
            #Add to total sum 
            R_Sum = R_Sum + 1/path_R
        #If there was a junction then calculate the total downstream resistance
        #using parallel resistor principle 
        if R_Sum != 0:
            G.node[edge[0]]["Total_R"] = 1/R_Sum
    '''

    '''
    check_edge = []
    print("Node Data: \n")
    for edge in edge_list:
        if edge[0] not in check_edge:
            check_edge.append(edge[0])
            print(edge[0])
            print(G.node[edge[0]])
            print("\n")
    '''
    ##############################################################################################################

    Multi_P = {}

    #Identifying and storing edges which will have the same P value
    #Key value is the multi_input that they're connected to
    for edge in edge_list:
        if(edge[1] in multi_inputs and multi_inputs[edge[1]] > 1):
            Multi_P[edge[1]] = []
            
    for edge in edge_list:
        if(edge[1] in multi_inputs and multi_inputs[edge[1]] > 1):
            current_edge_data = G.get_edge_data(edge[0],edge[1])
            Multi_P[edge[1]].append(current_edge_data)
    
    print("Multi_P")
    print(Multi_P)
    print("\n")

    #Correct Pressure Values in Graph
    for edge in edge_list:
        #If edge is connected to same sink then pressure value will be same. Eliminates any repeated trivial equations
        if(edge[1] in Multi_P):
            G[edge[0]][edge[1]][0]["pressure"].id = Multi_P[edge[1]][0][0]["pressure"].id
    
    #Set up Flow Rate Equations and Flow Rate Values in Edges 
    for edge in edge_list:
        for other_edge in edge_list:
            current_edge_data = G.get_edge_data(edge[0],edge[1])
            other_edge_data = G.get_edge_data(other_edge[0],other_edge[1])
            #Identify junction between edges and add previous edge flow rate to next edge if junction exists 
            if(edge[1] == other_edge[0] and current_edge_data[0]["pressure"].p_val == None):
                #Set up flow_eq attribute according to 3 main equations classes
                # if(current_edge_data[0]["flow_eq"] != None):
                #     print("fill in later")
                #Class 1: Input Port connected to edge so it's equal to input flow rate
                if(current_edge_data[0]["Port"] == "Source"):
                    current_edge_data[0]["flow_eq"] = {
                        "Class": 1,
                        "Positive": current_edge_data[0]["pressure"],
                        "Negative": other_edge_data[0]["pressure"],
                        "Resistance": resistance_data[edge[1]],
                    }
                #Class 3: Output Port connected to edge so constant is assigned b/c of known output pressure
                elif(other_edge_data[0]["Port"] == "Sink"):
                    neighbor_list = []
                    for neighbor in G.neighbors(edge[0]):
                        if neighbor != edge[1]:
                            neighbor_list.append(neighbor)
                    neighbor_list_2 = []
                    for neighbor in G.neighbors(edge[1]):
                        if neighbor != edge[0]:
                            neighbor_list_2.append(neighbor)
                    current_edge_data[0]["flow_eq"] = {
                        "Class": 3,
                        "Positive": current_edge_data[0]["pressure"],
                        "Negative": other_edge_data[0]["pressure"],
                        "Resistance": resistance_data[edge[1]],
                        "Source_Neighbors":neighbor_list,
                        "Sink_Neighbors":neighbor_list_2
                    }
                else:
                    neighbor_list = []
                    for neighbor in G.neighbors(edge[0]):
                        if neighbor != edge[1]:
                            neighbor_list.append(neighbor)
                    neighbor_list_2 = []
                    for neighbor in G.neighbors(edge[1]):
                        if neighbor != edge[0]:
                            neighbor_list_2.append(neighbor)
                    current_edge_data[0]["flow_eq"] = {
                        "Class": 2,
                        "Positive": current_edge_data[0]["pressure"],
                        "Negative": other_edge_data[0]["pressure"],
                        "Resistance": resistance_data[edge[1]],
                        "Source_Neighbors":neighbor_list,
                        "Sink_Neighbors":neighbor_list_2
                    }
                
###########################################################################################################################################################################
#ADJUSTMENTS TO BE MADE TO FORM SINGULAR MATRIX SYSTEM THAT WILL NOT NEED TO ACCOUNT FOR FLOW RATES 
###########################################################################################################################################################################

    #Initalize variables for matrix size and unknown P id's 
    size = 0
    Unknown_P = []

    #Allocate space for unknown matrices
    for edge in edge_list:
        current_edge_data = G.get_edge_data(edge[0],edge[1])
        if(current_edge_data[0]["flow_eq"] != None):
            #If pressure value is not already being solved for add to Unknown_P list 
            if(current_edge_data[0]["pressure"].id not in Unknown_P):
                Unknown_P.append(current_edge_data[0]["pressure"].id)
                size = size + 1
    
    print("Unknown_P")
    print(Unknown_P)

    #N = unknown P values 
    #Create NxN Matrix of known R values
    R_Matrix = np.zeros([size,size])
    #Create Nx1 Matrix of known values
    K_Matrix = np.zeros([size,1])

    #Initailize variables to be used in matrix formation
    row = 0
    P_Solved = []
    
    #Set up Resistance and Known Value Matrices 
    for edge in edge_list:

        #Get data from current edge
        current_edge_data = G.get_edge_data(edge[0],edge[1])
        #Check if row is within size of unknowns and that edge being analyzed has an unknown pressure value
        if(row < size and current_edge_data[0]["flow_eq"] != None):

            #Fill in matrices according to characteristics of class 1 equations
            if(current_edge_data[0]["flow_eq"]["Class"] == 1):
                
                print("CLASS 1 ROW: %i" % row)

                #Identify index of unknown P value and store positive, 1/R, value in same index in R_Matrix
                column = Unknown_P.index(current_edge_data[0]["flow_eq"]["Positive"].id)
                R_Matrix[row,column] = R_Matrix[row,column] + 1/current_edge_data[0]["flow_eq"]["Resistance"]
                
                #Identify index of unknown P value and store negative, -1/R, value in same index in R_Matrix
                column = Unknown_P.index(current_edge_data[0]["flow_eq"]["Negative"].id)
                R_Matrix[row,column] = R_Matrix[row,column] - 1/current_edge_data[0]["flow_eq"]["Resistance"]
                
                #Set known value of flow rate equal to equation
                K_Matrix[row,0] = current_edge_data[0]["flow"]
                
                #Equation is filled in so move to next row
                row = row + 1

            #Fill in matrices according to characteristics of class 3 equations
            elif(current_edge_data[0]["flow_eq"]["Class"] == 3):

                print("CLASS 3 ROW: %i" % row)
                ############## INFORMATION FROM CURRENT EDGE ##############
                
                #Identify index of unknown P value and store positive, 1/R, value in same index in R_Matrix
                column = Unknown_P.index(current_edge_data[0]["flow_eq"]["Positive"].id)
                R_Matrix[row,column] = R_Matrix[row,column] + 1/current_edge_data[0]["flow_eq"]["Resistance"]

                #Set equation equal to known constant of output pressure over junction resistance
                K_Matrix[row,0] = (101325)/current_edge_data[0]["flow_eq"]["Resistance"]
                
                ############## INFORMATION FROM CURRENT EDGE ##############

                ############## INFORMATION FROM PREVIOUS EDGE ##############

                #Check if there are multiple inputs to source node of edge
                if len(current_edge_data[0]["flow_eq"]["Source_Neighbors"]) > 1:
                    P_ids = []
                    #Loop through neighbors and store corresponding pressure values
                    for neighbor in current_edge_data[0]["flow_eq"]["Source_Neighbors"]:
                        edge_data = G.get_edge_data(neighbor,edge[0])
                        P_ids.append(edge_data[0]["pressure"].id)
                    #Check if there is only 1 unique input pressure from the multiple inputs
                    if len(set(P_ids)) == 1:
                        edge_data = G.get_edge_data(current_edge_data[0]["flow_eq"]["Source_Neighbors"][0],edge[0])
                        column = Unknown_P.index(edge_data[0]["flow_eq"]["Positive"].id)
                        R_Matrix[row,column] = R_Matrix[row,column] - 1/edge_data[0]["flow_eq"]["Resistance"]

                        column = Unknown_P.index(edge_data[0]["flow_eq"]["Negative"].id)
                        R_Matrix[row,column] = R_Matrix[row,column] + 1/edge_data[0]["flow_eq"]["Resistance"]
                    #If there is more than 1 unique input presssure
                    else:
                        #For each edge connected to source node of current edge include flow rate equations 
                        for neighbor in current_edge_data[0]["flow_eq"]["Source_Neighbors"]:
                            edge_data = G.get_edge_data(neighbor,edge[0])

                            column = Unknown_P.index(edge_data[0]["flow_eq"]["Positive"].id)
                            R_Matrix[row,column] = R_Matrix[row,column] - 1/edge_data[0]["flow_eq"]["Resistance"]

                            column = Unknown_P.index(edge_data[0]["flow_eq"]["Negative"].id)
                            R_Matrix[row,column] = R_Matrix[row,column] + 1/edge_data[0]["flow_eq"]["Resistance"]
                #If there is only 1 input to source node of edge 
                else:
                    edge_data = G.get_edge_data(current_edge_data[0]["flow_eq"]["Source_Neighbors"][0],edge[0])
                    column = Unknown_P.index(edge_data[0]["flow_eq"]["Positive"].id)
                    R_Matrix[row,column] = R_Matrix[row,column] - 1/edge_data[0]["flow_eq"]["Resistance"]

                    column = Unknown_P.index(edge_data[0]["flow_eq"]["Negative"].id)
                    R_Matrix[row,column] = R_Matrix[row,column] + 1/edge_data[0]["flow_eq"]["Resistance"]
                
                ############## INFORMATION FROM PREVIOUS EDGE ##############

                ############## INFORMATION FROM NEXT EDGE (NOT INCLUDED FROM CURRENT EDGE) ##############

                #Check if sink of edge was connected to another component other than a output port 
                if len(current_edge_data[0]["flow_eq"]["Sink_Neighbors"]) > 1:
                    print("FILL IN #2")

                #Set known value equal to constant value from known output port pressure value
                else:
                    print("FILL IN #4")
                
                ############## INFORMATION FROM NEXT EDGE (NOT INCLUDED FROM CURRENT EDGE) ##############
                
                #Equation is filled in so move to next row
                row = row + 1

            #Fill in matrices according to characteristics of class 2 equations
            elif(current_edge_data[0]["flow_eq"]["Class"] == 2):
                print("CLASS 2 ROW: %i" % row)

                if(current_edge_data[0]["pressure"].id not in P_Solved):
                    P_Solved.append(current_edge_data[0]["pressure"].id)
                    
                    ############## INFORMATION FROM CURRENT EDGE ##############
                    
                    #Identify index of unknown P value and store positive, 1/R, value in same index in R_Matrix
                    column = Unknown_P.index(current_edge_data[0]["flow_eq"]["Positive"].id)
                    R_Matrix[row,column] = R_Matrix[row,column] + 1/current_edge_data[0]["flow_eq"]["Resistance"]
                    #Identify index of unknown P value and store negative, -1/R, value in same index in R_Matrix
                    column = Unknown_P.index(current_edge_data[0]["flow_eq"]["Negative"].id)
                    R_Matrix[row,column] = R_Matrix[row,column] - 1/current_edge_data[0]["flow_eq"]["Resistance"]
                    
                    ############## INFORMATION FROM CURRENT EDGE ##############

                    ############## INFORMATION FROM OTHER EDGE ##############

                    if len(current_edge_data[0]["flow_eq"]["Sink_Neighbors"]) > 1:
                        for neighbor in current_edge_data[0]["flow_eq"]["Sink_Neighbors"]:
                            edge_data = G.get_edge_data(neighbor,edge[1])
                            if edge_data[0]["pressure"].id == current_edge_data[0]["pressure"].id:
                                for prev_neighbor in edge_data[0]["flow_eq"]["Source_Neighbors"]:
                                    prev_edge_data = G.get_edge_data(prev_neighbor,neighbor)
                                    column = Unknown_P.index(prev_edge_data[0]["flow_eq"]["Positive"].id)
                                    R_Matrix[row,column] = R_Matrix[row,column] - 1/prev_edge_data[0]["flow_eq"]["Resistance"]

                                    column = Unknown_P.index(prev_edge_data[0]["flow_eq"]["Negative"].id)
                                    R_Matrix[row,column] = R_Matrix[row,column] + 1/prev_edge_data[0]["flow_eq"]["Resistance"]
                    else:
                        print("FILL IN HERE 1")

                    ############## INFORMATION FROM OTHER EDGE ##############
                    
                    ############## INFORMATION FROM PREVIOUS EDGE ##############

                    if len(current_edge_data[0]["flow_eq"]["Source_Neighbors"]) > 1:
                        print("FILL IN HERE 2")
                    else:
                        edge_data = G.get_edge_data(current_edge_data[0]["flow_eq"]["Source_Neighbors"][0],edge[0])

                        column = Unknown_P.index(edge_data[0]["flow_eq"]["Positive"].id)
                        R_Matrix[row,column] = R_Matrix[row,column] - 1/edge_data[0]["flow_eq"]["Resistance"]

                        column = Unknown_P.index(edge_data[0]["flow_eq"]["Negative"].id)
                        R_Matrix[row,column] = R_Matrix[row,column] + 1/edge_data[0]["flow_eq"]["Resistance"]


                    ############## INFORMATION FROM PREVIOUS EDGE ##############

                    #Equation is filled in so move to next row
                    row = row + 1
                
                #Already included pressure as part of other equation so keep row the same 
                else:
                    row = row 
        
    counter = 1
    for edge in edge_list:
        print("Edge #%i" % counter)
        print(edge)
        current_edge_data = G.get_edge_data(edge[0],edge[1])
        print(current_edge_data)
        print("\n")
        counter = counter + 1
###########################################################################################################################################################################
#END OF ADJUSTMNETS 
###########################################################################################################################################################################
    
    
    print("\n")
    print("R_Matrix: ")
    print("\n")
    print(R_Matrix)
    print("\n")
    print("K_Matrix:")
    print("\n")
    K_Matrix = K_Matrix * ((1*pow(10,-6))/3600.)
    print(K_Matrix)
    #Convert flow rate from mL/hr to um^3/s
    #F_Matrix = F_Matrix * ((1*pow(10,-6))/3600.)
    print("\n")
    

    #Convert to Matrices
    R_Matrix = np.asmatrix(R_Matrix)
    K_Matrix = np.asmatrix(K_Matrix)

    #Calculate Value of Delta Pressure
    #Delta_P = np.linalg.solve(R_Matrix,K_Matrix)
    Delta_P = np.linalg.lstsq(R_Matrix,K_Matrix)

    
    print("Delta_P: ")
    print("\n")
    print(Delta_P)        
    print("\n")
    

    '''
    #Insert Pressure Values into Edges
    for edge in edge_list:
        current_edge_data = G.get_edge_data(edge[0],edge[1])
        counter = 0
        #For each value in Delta_P store pressure value if id matches correct Unknown_P index 
        for pressure in Delta_P:
            if(Unknown_P[counter] == current_edge_data[0]["pressure"].id):
                current_edge_data[0]["pressure"].p_val = Delta_P[counter,0]
            counter = counter + 1
    '''
    
    '''
    print("Final Edge List with Data: ")
    print("\n")
    counter = 1
    for edge in G.edges.data():
        print("Edge %i: " % counter)
        print(edge)
        print("\n")
        counter = counter + 1
    '''

    '''
    for node in G.nodes():
        for degree in degrees:
            if(node == degree):
                print(degrees[node])
    
    #Print Statements 
    print("EDGES: ")
    print(G.edges.data())
    print("\n")
    
    print("********* COMPONENTS *********")
    print("\n")
    for component in components:
        print(component)
        print("\n")
    
    print("********* CONNECTIONS *********")
    print("\n")
    for connection in connections:
        print(connection)
        print("\n")

    print("********* TARGETS *********")
    print("\n")
    for target in targets:
        print(target)
        print("\n")
    '''
    print("********* RESISTANCE DICTIONARY *********")
    print(resistance_data)
    print("\n")
    
    return G