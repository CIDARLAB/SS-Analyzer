from flask import Flask, jsonify, abort, make_response, request
import networkx as nx
import json
import numpy as np
import enum
import Channel_Resistance
import Mixer_Resistance

#JSON Parser is designed to form primitive graph connections and then save corresponding data

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

#Define JSON classes 
class Component:

        def __init__(self,name,layers,ID,params,ports,entity):
            self.name = name
            self.layers = layers
            self.id = ID
            self.params = params
            self.ports = ports
            self.entity = entity

        def __str__(self):
            return str(self.__dict__)

        def __repr__(self):
            return str(self.__dict__)

class Connection:

    def __init__(self,sinks,name,ID,source,params,layer):
        self.sinks = sinks
        self.name = name
        self.id = ID
        self.source = source
        self.params = params
        self.layer = layer 

    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

class Port:

    def __init__(self,x,y,label,layer):
        self.x = x
        self.y = y
        self.label = label
        self.layer = layer

    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)


class Target:

    def __init__(self,component,port):
        self.component = component
        self.port = port

    def __str__(self):
        return str(self.__dict__)

class Pressure:

    def __init__(self,id,pressure):
        self.id = id
        self.p_val = pressure
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

#**********************************************************************************************************************************

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

#**********************************************************************************************************************************

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})

#**********************************************************************************************************************************

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    
    if not request.json:
        abort(400)

    #Implementation of back end code 
    
    #Initialize Variables
    #parsed_JSON = json.load(open('JSON_Tests/test.json'))
    parsed_JSON = request.get_json()
    G = nx.MultiGraph()
    components = []
    connections = []
    targets = []
    resistance_data = {}
    primitive_res = 0

    #Iterate through components and save as Component Objects
    for component in parsed_JSON["components"]:
        name = component["name"]
        layers = component["layers"]
        ID = component["id"]
        params = component["params"]
        ports = component["ports"]
        entity = component["entity"]
        num_ports = len(component["ports"])
        
        #Reset list of Port Objects 
        ports_to_add = []

        #For each component save port data as Port Object
        if(num_ports != 0):
            for port in ports:
                x = port["x"]
                y = port["y"]
                label = port["label"]
                layer = port["layer"]
                
                #Append list of Port Objects
                ports_to_add.append(Port(x,y,label,layer))

                #Append list of Target Objects 
                targets.append(Target(ID,Port(x,y,label,layer)))
        
        #Append list of Component Objects using list of Port Objects 
        components.append(Component(name,layers,ID,params,ports_to_add,entity))

    #Iterate through connections and save as Component Objects 
    for connection in parsed_JSON["connections"]:
        sinks = connection["sinks"]
        name = connection["name"]
        ID = connection["id"]
        source = connection["source"]
        params = connection["params"]
        layer = connection["layer"]

        #Append list of Connection Objects 
        connections.append(Connection(sinks,name,ID,source,params,layer))

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


    #For each component connect to channel and vice versa and include resistance values in graph 
    for component in parsed_JSON["components"]:
        for connection in parsed_JSON["connections"]:
            #Create edges from source to primitive 
            if(component["id"] == connection["source"]["component"]):
                #If Port is source flow rate is equal to the flow in
                if(component["entity"] == "PORT"):
                    G.add_edge(component["id"],connection["name"], pressure = Pressure(component["name"],None) , flow_eq = None, flow = 1.)
                #All other cases
                else:
                    G.add_edge(connection["name"],component["id"], pressure = Pressure(connection["name"],None), flow_eq = None, flow = 0.)   
            #Create edges from primitive to sinks
            if(component["id"] == connection["sinks"][0]["component"]):
                #If Port is sink it is a final output and you can set the pressure to atm pressure (Pa)
                if(component["entity"] == "PORT"):
                    #101325 Pa is atmospheric pressure 
                    G.add_edge(connection["name"],component["id"], pressure = Pressure(component["name"],101325), flow_eq = None, flow = 0.)
                #All other cases 
                else:
                    G.add_edge(connection["name"],component["id"], pressure = Pressure(component["name"],None), flow_eq = None, flow = 0.)

    #Create edge_list object
    edge_list = G.edges()
    #Initialize dict which stores how many outputs each primitive has
    multi_outputs = {}
    multi_inputs = {}

    #Establish how many primitives have multiple outputs to divide flow rate 
    for edge in edge_list:
        
        #Set Node Junction Attribute to be false initatially 
        G.node[edge[0]]["Junction"] = False
        G.node[edge[0]]["Total_R"] = None
        G.node[edge[0]]["R_Paths"] = {}
        G.node[edge[0]]["R_Paths_Value"] = {}

        #Store key as source id and save with 1 output 
        if(edge[0] not in multi_outputs):
            multi_outputs[edge[0]] = 1
        #If key is already in dict then it means it is another source and will lead to another output
        elif(edge[0] in multi_outputs):
            multi_outputs[edge[0]] = multi_outputs[edge[0]] + 1
        
        if(edge[1] not in multi_inputs):
            multi_inputs[edge[1]] = 1
        elif(edge[1] in multi_inputs):
            multi_inputs[edge[1]] = multi_inputs[edge[1]] + 1
    
    #EXPERIMENTAL STUFF
    ##############################################################################################################

    print("\n")
    print("MULTI OUTPUTS: ")
    print(multi_outputs)
    print("\n")
    print("MULTI INPUTS: ")
    print(multi_inputs)
    print("\n")

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
    
    # for edge in edge_list:
    #     for path in G.node[edge[0]]["R_Paths"]:
    #         for comp in G.node[edge[0]]["R_Paths"][path]:
    #             if G.node[edge[0]]["Total_R"] == None:
    #                 G.node[edge[0]]["Total_R"] = resistance_data[comp]
    #             #STILL NEEDS TO ACCOUNT FOR INSTANCES WHEN IT MEETS UP WITH OTHER JUNCTIONS
    #             #elif comp != "port_out":
    #             #    if G.node[comp]["Junction"] == True:
    #             #        G.node[edge[0]]["Total_R"] = G.node[edge[0]]["Total_R"] + G.node[comp]["Total_R"]
    #             else:
    #                 G.node[edge[0]]["Total_R"] = G.node[edge[0]]["Total_R"] + resistance_data[comp]
    
    
    #DOESN'T ACCOUNT FOR OTHER JUNCTIONS DOWNSTREAM
    for edge in edge_list:
        R_Sum = 0
        for path in G.node[edge[0]]["R_Paths"]:
            #Path is equal to key of path stored under R_Paths
            path_R = 0
            start = 0
            for comp in G.node[edge[0]]["R_Paths"][path]:
                #Do not include the path's starting resistance 
                if start > 0:
                    #NEEDS TO ACCOUNT FOR OTHER JUNCTIONS THAT LIE POTENTIALLY DOWNSTREAM
                    path_R = path_R + resistance_data[comp]
                    start = start + 1
                else:
                    start = start + 1
            #Set Path Resistance
            G.node[edge[0]]["R_Paths_Value"][path] = path_R
            #Add to total sum 
            R_Sum = R_Sum + 1/path_R
        #If there was a junction then calculate the total downstream resistance
        #using parallel resistor principle 
        if R_Sum != 0:
            G.node[edge[0]]["Total_R"] = 1/R_Sum


    check_edge = []
    print("Node Data: \n")
    for edge in edge_list:
        if edge[0] not in check_edge:
            check_edge.append(edge[0])
            print(edge[0])
            print(G.node[edge[0]])
            print("\n")

    ##############################################################################################################

    
    #Set up Flow Rate Equations and Flow Rate Values in Edges 
    for edge in edge_list:
        for other_edge in edge_list:
            current_edge_data = G.get_edge_data(edge[0],edge[1])
            other_edge_data = G.get_edge_data(other_edge[0],other_edge[1])
            #Identify junction between edges and add previous edge flow rate to next edge if junction exists 
            if(edge[1] == other_edge[0]):
                #Output flow rate is divided based on how many components connected at junction
                G[other_edge[0]][other_edge[1]][0]["flow"] = G[other_edge[0]][other_edge[1]][0]["flow"]  + (G[edge[0]][edge[1]][0]["flow"] /multi_outputs[edge[0]])
                #Set up equation in flow attribute if the pressure is not pre-defined
                if(current_edge_data[0]["pressure"].p_val == None):
                    current_edge_data[0]["flow_eq"] = {
                        "Positive": current_edge_data[0]["pressure"],
                        "Negative": other_edge_data[0]["pressure"],
                        "Resistance": resistance_data[edge[1]]
                    }

    #Initalize variables for matrix size and unknown P id's 
    size = 0
    unknown_P = []

    #Allocate space for unknown matrices
    for edge in edge_list:
        current_edge_data = G.get_edge_data(edge[0],edge[1])
        if(current_edge_data[0]["flow_eq"] != None):
            #If pressure value is not already being solved for add to unknown_P list 
            if(current_edge_data[0]["pressure"].id not in unknown_P):
                unknown_P.append(current_edge_data[0]["pressure"].id)
                size = size + 1
    

    #N = unknown P values 
    #Create NxN Matrix of known R values
    R_Matrix = np.zeros([size,size])
    #Create Nx1 Matrix of known F values
    F_Matrix = np.zeros([size,1])

    row = 0

    #Set up Resistance and Flow Rate Matrices 
    for edge in edge_list:
        #Get data from selected edge
        current_edge_data = G.get_edge_data(edge[0],edge[1])
        #Initalize Variables
        column = 0
        check1 = False
        check2 = False
        #Check if these is a flow rate equation and if there are enough equations to solve unknowns
        if(current_edge_data[0]["flow_eq"] != None and row < size):
            #Iterate through unknown P id's and check where postiive and negative values from equation should be placed
            for P_Solve in unknown_P:
                if(current_edge_data[0]["flow_eq"]["Positive"].id == P_Solve):
                    F_Matrix[row,0] = current_edge_data[0]["flow"]
                    #Check if the positive resistance value is already located in same column as another equation
                    for check_row in R_Matrix:
                        if(check_row[column] == 1/current_edge_data[0]["flow_eq"]["Resistance"]):
                            check1 = True
                    #If the other pressure value is unknown just add to R_Matrix
                    if(current_edge_data[0]["flow_eq"]["Negative"].p_val == None):
                        R_Matrix[row,column] = 1/current_edge_data[0]["flow_eq"]["Resistance"]
                    #If the other pressure value is constance add to R_Matrix and adjust the F_Matrix
                    else:
                        R_Matrix[row,column] = 1/current_edge_data[0]["flow_eq"]["Resistance"]
                        F_Matrix[row,0] = F_Matrix[row,0] + current_edge_data[0]["flow_eq"]["Negative"].p_val/current_edge_data[0]["flow_eq"]["Resistance"]
                    column = column + 1
                elif(current_edge_data[0]["flow_eq"]["Negative"].id == P_Solve):
                    F_Matrix[row,0] = current_edge_data[0]["flow"]
                    #Check if the negative resistance value is already located in same column as another equation
                    for check_row in R_Matrix:
                        if(check_row[column] == -1/current_edge_data[0]["flow_eq"]["Resistance"]):
                            check2 = True
                    #If the other pressure value is unknown just add to R_Matrix
                    if(current_edge_data[0]["flow_eq"]["Positive"].p_val == None):
                        R_Matrix[row,column] = -1/current_edge_data[0]["flow_eq"]["Resistance"]
                    #If the other pressure value is constance add to R_Matrix and adjust the F_Matrix
                    else:
                        R_Matrix[row,column] = -1/current_edge_data[0]["flow_eq"]["Resistance"]
                        F_Matrix[row,0] = F_Matrix[row,0] - current_edge_data[0]["flow_eq"]["Positive"].p_val/current_edge_data[0]["flow_eq"]["Resistance"]
                    column = column + 1
                #No id matches unknown presssure
                else:
                    column = column + 1
            #Both checks true if a row is repeated
            if(check1 == True and check2 == True):
                #Clear row and will in with next equation
                R_Matrix[row] = 0
                row = row
            else:
                row = row + 1

    '''
    print("\n")
    print("R_Matrix: ")
    print("\n")
    print(R_Matrix)
    print("\n")
    print("F_Matrix:")
    print("\n")
    #Convert flow rate from mL/hr to um^3/s
    F_Matrix = F_Matrix * ((1*pow(10,-6))/3600.)
    print(F_Matrix)
    print("\n")
    '''

    #Convert to Matrices
    R_Matrix = np.asmatrix(R_Matrix)
    F_Matrix = np.asmatrix(F_Matrix)

    #Calculate Value of Delta Pressure
    Delta_P = np.linalg.inv(R_Matrix) * F_Matrix

    '''
    print("Delta_P: ")
    print("\n")
    print(Delta_P)        
    print("\n")
    '''

    #Insert Pressure Values into Edges
    for edge in edge_list:
        current_edge_data = G.get_edge_data(edge[0],edge[1])
        counter = 0
        #For each value in Delta_P store pressure value if id matches correct unknown_P index 
        for pressure in Delta_P:
            if(unknown_P[counter] == current_edge_data[0]["pressure"].id):
                current_edge_data[0]["pressure"].p_val = Delta_P[counter,0]
            counter = counter + 1
    
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

    print("********* RESISTANCE DICTIONARY *********")
    print(resistance_data)
    print("\n")
    '''

    return jsonify(parsed_JSON),201

#**********************************************************************************************************************************

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})

#**********************************************************************************************************************************

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})

#**********************************************************************************************************************************

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#**********************************************************************************************************************************

if __name__ == '__main__':
    from flask import Flask, jsonify, abort, make_response, request
import networkx as nx
import json
import numpy as np
import enum
import Channel_Resistance
import Mixer_Resistance

#JSON Parser is designed to form primitive graph connections and then save corresponding data

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

#Define JSON classes 
class Component:

        def __init__(self,name,layers,ID,params,ports,entity):
            self.name = name
            self.layers = layers
            self.id = ID
            self.params = params
            self.ports = ports
            self.entity = entity

        def __str__(self):
            return str(self.__dict__)

        def __repr__(self):
            return str(self.__dict__)

class Connection:

    def __init__(self,sinks,name,ID,source,params,layer):
        self.sinks = sinks
        self.name = name
        self.id = ID
        self.source = source
        self.params = params
        self.layer = layer 

    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

class Port:

    def __init__(self,x,y,label,layer):
        self.x = x
        self.y = y
        self.label = label
        self.layer = layer

    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)


class Target:

    def __init__(self,component,port):
        self.component = component
        self.port = port

    def __str__(self):
        return str(self.__dict__)

class Pressure:

    def __init__(self,id,pressure):
        self.id = id
        self.p_val = pressure
    
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

#**********************************************************************************************************************************

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

#**********************************************************************************************************************************

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})

#**********************************************************************************************************************************

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
    
    if not request.json:
        abort(400)

    #Implementation of back end code 
    
    #Initialize Variables
    #parsed_JSON = json.load(open('JSON_Tests/test.json'))
    parsed_JSON = request.get_json()
    G = nx.MultiGraph()
    components = []
    connections = []
    targets = []
    resistance_data = {}
    primitive_res = 0

    #Iterate through components and save as Component Objects
    for component in parsed_JSON["components"]:
        name = component["name"]
        layers = component["layers"]
        ID = component["id"]
        params = component["params"]
        ports = component["ports"]
        entity = component["entity"]
        num_ports = len(component["ports"])
        
        #Reset list of Port Objects 
        ports_to_add = []

        #For each component save port data as Port Object
        if(num_ports != 0):
            for port in ports:
                x = port["x"]
                y = port["y"]
                label = port["label"]
                layer = port["layer"]
                
                #Append list of Port Objects
                ports_to_add.append(Port(x,y,label,layer))

                #Append list of Target Objects 
                targets.append(Target(ID,Port(x,y,label,layer)))
        
        #Append list of Component Objects using list of Port Objects 
        components.append(Component(name,layers,ID,params,ports_to_add,entity))

    #Iterate through connections and save as Component Objects 
    for connection in parsed_JSON["connections"]:
        sinks = connection["sinks"]
        name = connection["name"]
        ID = connection["id"]
        source = connection["source"]
        params = connection["params"]
        layer = connection["layer"]

        #Append list of Connection Objects 
        connections.append(Connection(sinks,name,ID,source,params,layer))

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


    #For each component connect to channel and vice versa and include resistance values in graph 
    for component in parsed_JSON["components"]:
        for connection in parsed_JSON["connections"]:
            #Create edges from source to primitive 
            if(component["id"] == connection["source"]["component"]):
                #If Port is source flow rate is equal to the flow in
                if(component["entity"] == "PORT"):
                    G.add_edge(component["id"],connection["name"], pressure = Pressure(component["name"],None) , flow_eq = None, flow = 1.)
                #All other cases
                else:
                    G.add_edge(connection["name"],component["id"], pressure = Pressure(connection["name"],None), flow_eq = None, flow = 0.)   
            #Create edges from primitive to sinks
            if(component["id"] == connection["sinks"][0]["component"]):
                #If Port is sink it is a final output and you can set the pressure to atm pressure (Pa)
                if(component["entity"] == "PORT"):
                    #101325 Pa is atmospheric pressure 
                    G.add_edge(connection["name"],component["id"], pressure = Pressure(component["name"],101325), flow_eq = None, flow = 0.)
                #All other cases 
                else:
                    G.add_edge(connection["name"],component["id"], pressure = Pressure(component["name"],None), flow_eq = None, flow = 0.)

    #Create edge_list object
    edge_list = G.edges()
    #Initialize dict which stores how many outputs each primitive has
    multi_outputs = {}
    multi_inputs = {}

    #Establish how many primitives have multiple outputs to divide flow rate 
    for edge in edge_list:
        
        #Set Node Junction Attribute to be false initatially 
        G.node[edge[0]]["Junction"] = False
        G.node[edge[0]]["Total_R"] = None
        G.node[edge[0]]["R_Paths"] = {}
        G.node[edge[0]]["R_Paths_Value"] = {}

        #Store key as source id and save with 1 output 
        if(edge[0] not in multi_outputs):
            multi_outputs[edge[0]] = 1
        #If key is already in dict then it means it is another source and will lead to another output
        elif(edge[0] in multi_outputs):
            multi_outputs[edge[0]] = multi_outputs[edge[0]] + 1
        
        if(edge[1] not in multi_inputs):
            multi_inputs[edge[1]] = 1
        elif(edge[1] in multi_inputs):
            multi_inputs[edge[1]] = multi_inputs[edge[1]] + 1
    
    #EXPERIMENTAL STUFF
    ##############################################################################################################

    print("\n")
    print("MULTI OUTPUTS: ")
    print(multi_outputs)
    print("\n")
    print("MULTI INPUTS: ")
    print(multi_inputs)
    print("\n")

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
    
    # for edge in edge_list:
    #     for path in G.node[edge[0]]["R_Paths"]:
    #         for comp in G.node[edge[0]]["R_Paths"][path]:
    #             if G.node[edge[0]]["Total_R"] == None:
    #                 G.node[edge[0]]["Total_R"] = resistance_data[comp]
    #             #STILL NEEDS TO ACCOUNT FOR INSTANCES WHEN IT MEETS UP WITH OTHER JUNCTIONS
    #             #elif comp != "port_out":
    #             #    if G.node[comp]["Junction"] == True:
    #             #        G.node[edge[0]]["Total_R"] = G.node[edge[0]]["Total_R"] + G.node[comp]["Total_R"]
    #             else:
    #                 G.node[edge[0]]["Total_R"] = G.node[edge[0]]["Total_R"] + resistance_data[comp]
    
    
    #DOESN'T ACCOUNT FOR OTHER JUNCTIONS DOWNSTREAM
    for edge in edge_list:
        R_Sum = 0
        for path in G.node[edge[0]]["R_Paths"]:
            #Path is equal to key of path stored under R_Paths
            path_R = 0
            start = 0
            for comp in G.node[edge[0]]["R_Paths"][path]:
                #Do not include the path's starting resistance 
                if start > 0:
                    #NEEDS TO ACCOUNT FOR OTHER JUNCTIONS THAT LIE POTENTIALLY
                    path_R = path_R + resistance_data[comp]
                    start = start + 1
                else:
                    start = start + 1
            #Set Path Resistance
            G.node[edge[0]]["R_Paths_Value"][path] = path_R
            #Add to total sum 
            R_Sum = R_Sum + 1/path_R
        #If there was a junction then calculate the total downstream resistance
        #using parallel resistor principle 
        if R_Sum != 0:
            G.node[edge[0]]["Total_R"] = 1/R_Sum



    check_edge = []
    print("Node Data: \n")
    for edge in edge_list:
        if edge[0] not in check_edge:
            check_edge.append(edge[0])
            print(edge[0])
            print(G.node[edge[0]])
            print("\n")

    ##############################################################################################################

    
    #Set up Flow Rate Equations and Flow Rate Values in Edges 
    for edge in edge_list:
        for other_edge in edge_list:
            current_edge_data = G.get_edge_data(edge[0],edge[1])
            other_edge_data = G.get_edge_data(other_edge[0],other_edge[1])
            #Identify junction between edges and add previous edge flow rate to next edge if junction exists 
            if(edge[1] == other_edge[0]):
                #Output flow rate is divided based on how many components connected at junction
                G[other_edge[0]][other_edge[1]][0]["flow"] = G[other_edge[0]][other_edge[1]][0]["flow"]  + (G[edge[0]][edge[1]][0]["flow"] /multi_outputs[edge[0]])
                #Set up equation in flow attribute if the pressure is not pre-defined
                if(current_edge_data[0]["pressure"].p_val == None):
                    current_edge_data[0]["flow_eq"] = {
                        "Positive": current_edge_data[0]["pressure"],
                        "Negative": other_edge_data[0]["pressure"],
                        "Resistance": resistance_data[edge[1]]
                    }

    #Initalize variables for matrix size and unknown P id's 
    size = 0
    unknown_P = []

    #Allocate space for unknown matrices
    for edge in edge_list:
        current_edge_data = G.get_edge_data(edge[0],edge[1])
        if(current_edge_data[0]["flow_eq"] != None):
            #If pressure value is not already being solved for add to unknown_P list 
            if(current_edge_data[0]["pressure"].id not in unknown_P):
                unknown_P.append(current_edge_data[0]["pressure"].id)
                size = size + 1
    

    #N = unknown P values 
    #Create NxN Matrix of known R values
    R_Matrix = np.zeros([size,size])
    #Create Nx1 Matrix of known F values
    F_Matrix = np.zeros([size,1])

    row = 0

    #Set up Resistance and Flow Rate Matrices 
    for edge in edge_list:
        #Get data from selected edge
        current_edge_data = G.get_edge_data(edge[0],edge[1])
        #Initalize Variables
        column = 0
        check1 = False
        check2 = False
        #Check if these is a flow rate equation and if there are enough equations to solve unknowns
        if(current_edge_data[0]["flow_eq"] != None and row < size):
            #Iterate through unknown P id's and check where postiive and negative values from equation should be placed
            for P_Solve in unknown_P:
                if(current_edge_data[0]["flow_eq"]["Positive"].id == P_Solve):
                    F_Matrix[row,0] = current_edge_data[0]["flow"]
                    #Check if the positive resistance value is already located in same column as another equation
                    for check_row in R_Matrix:
                        if(check_row[column] == 1/current_edge_data[0]["flow_eq"]["Resistance"]):
                            check1 = True
                    #If the other pressure value is unknown just add to R_Matrix
                    if(current_edge_data[0]["flow_eq"]["Negative"].p_val == None):
                        R_Matrix[row,column] = 1/current_edge_data[0]["flow_eq"]["Resistance"]
                    #If the other pressure value is constance add to R_Matrix and adjust the F_Matrix
                    else:
                        R_Matrix[row,column] = 1/current_edge_data[0]["flow_eq"]["Resistance"]
                        F_Matrix[row,0] = F_Matrix[row,0] + current_edge_data[0]["flow_eq"]["Negative"].p_val/current_edge_data[0]["flow_eq"]["Resistance"]
                    column = column + 1
                elif(current_edge_data[0]["flow_eq"]["Negative"].id == P_Solve):
                    F_Matrix[row,0] = current_edge_data[0]["flow"]
                    #Check if the negative resistance value is already located in same column as another equation
                    for check_row in R_Matrix:
                        if(check_row[column] == -1/current_edge_data[0]["flow_eq"]["Resistance"]):
                            check2 = True
                    #If the other pressure value is unknown just add to R_Matrix
                    if(current_edge_data[0]["flow_eq"]["Positive"].p_val == None):
                        R_Matrix[row,column] = -1/current_edge_data[0]["flow_eq"]["Resistance"]
                    #If the other pressure value is constance add to R_Matrix and adjust the F_Matrix
                    else:
                        R_Matrix[row,column] = -1/current_edge_data[0]["flow_eq"]["Resistance"]
                        F_Matrix[row,0] = F_Matrix[row,0] - current_edge_data[0]["flow_eq"]["Positive"].p_val/current_edge_data[0]["flow_eq"]["Resistance"]
                    column = column + 1
                #No id matches unknown presssure
                else:
                    column = column + 1
            #Both checks true if a row is repeated
            if(check1 == True and check2 == True):
                #Clear row and will in with next equation
                R_Matrix[row] = 0
                row = row
            else:
                row = row + 1

    '''
    print("\n")
    print("R_Matrix: ")
    print("\n")
    print(R_Matrix)
    print("\n")
    print("F_Matrix:")
    print("\n")
    #Convert flow rate from mL/hr to um^3/s
    F_Matrix = F_Matrix * ((1*pow(10,-6))/3600.)
    print(F_Matrix)
    print("\n")
    '''

    #Convert to Matrices
    R_Matrix = np.asmatrix(R_Matrix)
    F_Matrix = np.asmatrix(F_Matrix)

    #Calculate Value of Delta Pressure
    Delta_P = np.linalg.inv(R_Matrix) * F_Matrix

    '''
    print("Delta_P: ")
    print("\n")
    print(Delta_P)        
    print("\n")
    '''

    #Insert Pressure Values into Edges
    for edge in edge_list:
        current_edge_data = G.get_edge_data(edge[0],edge[1])
        counter = 0
        #For each value in Delta_P store pressure value if id matches correct unknown_P index 
        for pressure in Delta_P:
            if(unknown_P[counter] == current_edge_data[0]["pressure"].id):
                current_edge_data[0]["pressure"].p_val = Delta_P[counter,0]
            counter = counter + 1
    
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

    print("********* RESISTANCE DICTIONARY *********")
    print(resistance_data)
    print("\n")
    '''

    return jsonify(parsed_JSON),201

#**********************************************************************************************************************************

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['title'] = request.json.get('title', task[0]['title'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})

#**********************************************************************************************************************************

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})

#**********************************************************************************************************************************

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#**********************************************************************************************************************************

if __name__ == '__main__':
    app.run(debug=True)