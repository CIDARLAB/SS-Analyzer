from typing import List, Optional
from ufssanalyzer.electrical.eNetwork import ENetwork
import numpy as np

from ufssanalyzer.solver.flowEquation import FlowEquation


class Solver:
    """The Solver class can be used to solve a system of equations.

    How to use the solver class:
    1. use `initialize` for the solver to formulate the Flow Equations at each of the CPoints
    2. use `solve` for the solver to construct the matrices and then solve the entire system of equations
    """

    def __init__(self):
        self.flowRateEquations: List[FlowEquation] = []
        self.eNetwork: Optional[ENetwork] = None

    def initialize(self, enetwork: ENetwork) -> None:
        """Initialize the solver with the ENetwork

        This method goes ahead and gernates all the flow equations
        at each of the CPoints. This is equal to the node equations
        seen in electrical networks.

        Args:
            enetwork (ENetwork): [description]
        """
        # Setup Flow Equations for each of the calculation points
        # print(enetwork.iocalculationPoints)
        # print(enetwork.internalCalculationPoints)

        self.eNetwork = enetwork

        print("Setting up Flow Rate Equations")
        for key in enetwork.io_calculation_points.keys():
            cpoint = enetwork.io_calculation_points[key]

            # Do not construct equation if pressure is known
            if cpoint.pressure == None:
                equation = FlowEquation.constructFlowEquation(enetwork, cpoint)
                self.flowRateEquations.append(equation)

        for key in enetwork.internal_calculation_points.keys():
            cpoint = enetwork.internal_calculation_points[key]

            # Do not construct equation if pressure is known
            if cpoint.pressure == None:
                equation = FlowEquation.constructFlowEquation(enetwork, cpoint)
                self.flowRateEquations.append(equation)

    def solve(self) -> None:
        """Solves the system of equations that are set up in the form of
        FlowEquation objects.

        The method sets up the matrices (Ax = B) and then utilizes numpy's
        linear solver to solve the matrices and repopulate the ENetwork.
        """

        # Setup the Matrices for the Solver
        # Run through each of the equations and start setting up the matrices
        # A Matrix in AX = B

        print("Constructing Matrices...")
        size = len(self.flowRateEquations)
        A = np.zeros([size, size])
        B = np.zeros([size, 1])

        eqindex = [equation.unknown for equation in self.flowRateEquations]

        # Populate teh Matrices
        for i in range(len(self.flowRateEquations)):
            equation = self.flowRateEquations[i]
            A[i, i] = equation.multiplier
            B[i] = equation.constantterm

            for key in equation.neighbourterms.keys():
                # Find where this key is
                where = eqindex.index(key)
                value = equation.neighbourterms[key]
                A[i, where] = value

        print("A: ")
        print(A)
        print("B: ")
        print(B)
        # Solve the Matrices
        print("Solving System...")
        X = np.linalg.solve(A, B)

        print("X: ")
        print(X)

        print("Updating ENetwork...")
        for i in range(len(eqindex)):
            self.eNetwork.update_pressure(eqindex[i], X[i, 0])
