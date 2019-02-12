from .flowEquation import FlowEquation

class NewSolver:

    def __init__(self):
        self.flowRateEquations = []


    def initialize(self, enetwork):
        #Setup Flow Equations for each of the calculation points
        print(enetwork.iocalculationPoints)
        print(enetwork.internalCalculationPoints)
        
        for key in enetwork.iocalculationPoints.keys():
            cpoint = enetwork.iocalculationPoints[key]

            #Do not construct equation if pressure is known
            if cpoint.pressure == None:
                equation = FlowEquation.constructFlowEquation(enetwork, cpoint)
                self.flowRateEquations.append(equation)

        for key in enetwork.internalCalculationPoints.keys():
            cpoint = enetwork.internalCalculationPoints[key]

            #Do not construct equation if pressure is known
            if cpoint.pressure == None:
                equation = FlowEquation.constructFlowEquation(enetwork, cpoint)
                self.flowRateEquations.append(equation)
    
    def solve(self):
        #Setup the Matrices for the Solver

        #Solve the Matrices
        pass