pressureDict = dict() 
flowrateDict = dict() 
inletOutletDict = dict()

def setPressure(name, pressure):
    pressureDict[name] = pressure

def getPressure(name):
    return pressureDict[name]

def setFlowRate(name, flowrate):
    flowrateDict[name] = flowrate

def getFlowRate(name):
    return flowrateDict[name]

def setInletOutlet(name, state):
    inletOutletDict[name] = state

def getInletOutlet(name):
    return inletOutletDict[name]

def parseConfig(file):

    lines = file.read().splitlines()
    for line in lines: 
        line = line.strip()
        parts = line.split(',')
        name = parts[0].strip()
        state = parts[1].strip()
        value = parts[2].strip()
        setInletOutlet(name, state)
        if state == "IN":
            setFlowRate(name, float(value))
        elif state == "OUT":
            setPressure(name, float(value))
        else:
            print('Unkown state:', state)
    file.close()
