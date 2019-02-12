import numpy as np

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
        #Run through each of the equations and start setting up the matrices
        #A Matrix in AX = B
        size = len(self.flowRateEquations)
        A = np.zeros([size, size])
        B = np.zeros([size, 1])

        eqindex = [ equation.unknown for equation in self.flowRateEquations ]
        
        for i in range(len(self.flowRateEquations)):
            equation = self.flowRateEquations[i]
            A[i, i] = equation.multiplier
            B[i] = equation.constantterm

            for key in equation.neighbourterms.keys():
                #Find where this key is
                where = eqindex.index(key)
                value = equation.neighbourterms[key]
                A[i, where] = value

        print("A: ")
        print(A)
        print("B: ")
        print(B)

        X = np.linalg.solve(A, B)

        print("X: ")
        print(X)
            

        #Solve the Matrices
        pass


    def annotate(self):
        #Update all the solution values
        pass
