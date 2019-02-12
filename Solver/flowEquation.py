class FlowEquation:
    def __init__(self):
        self.unknown = None
        self.multiplier = 0
        self.neighbourterms = dict()
        
        # There are also the known values in the system of equations
        self.constantterm = 0

    @staticmethod
    def constructFlowEquation(enetwork, cpoint):
        print("Contruct Equation for CPoint: ", cpoint.id)
        #if cpoint pressure is known, then skip the construction
        if cpoint.pressure != None:
            raise Exception("Should not construct equation if cpoint is known")
        
        #if CPoint has a known flow rate 
        if cpoint.flowrate != None:
            print("Construct Type 1 Equation...")
            # this means that it has a known flowrate
            ret = FlowEquation.constructType1Equation(enetwork, cpoint)
            return ret

        #Examine the neighbours to see if it has a known input or an output    
        neighbors = enetwork.G.neighbors(cpoint.id)
        for key in neighbors:
            neighbor = enetwork.getCPoint(key)
            # print( "n- ", key, cpoint)

            #if neighbour is output classify as type 3. this means that it has a known pressure
            if neighbor.flowrate == None and neighbor.pressure != None:
                print("Construct Type 3 Equation...")
                ret = FlowEquation.constructType3Equation(enetwork, cpoint)
                return ret
            
        #end neighbour examination

        #If this is running it means that it has no inputs or outputs and we are dealing with an internal point
        print("Construct Type 2 Equation...")
        ret = FlowEquation.constructType2Equation(enetwork, cpoint)
        return ret


    @staticmethod
    def constructType1Equation(enetwork, cpoint):
        ret = FlowEquation()
        ret.unknown = cpoint.id

        #Add the flow rate to the constant term
        ret.constantterm += cpoint.flowrate

        #go through the neighbours
        neighbors = enetwork.G.neighbors(cpoint.id)
        # print("neighbours of ", cpoint.id)

        for key in neighbors:
            neighbor = enetwork.getCPoint(key)

            #if neighbour is input
            if neighbor.flowrate != None and neighbor.pressure == None:
                #Create Constant Term with this itself
                ret.constantterm += neighbor.flowrate

            elif neighbor.flowrate == None and neighbor.pressure != None:
                R = enetwork.getResistanceBetween(cpoint.id, neighbor.id)
                ret.neighbourterms[neighbor.id] = -1/R
                ret.constantterm += 1/R

            elif neighbor.pressure != None:
                print("Error CPoint: ", neighbor)
                raise Exception("Don't know how to handle this situation")

            else:
                R = enetwork.getResistanceBetween(cpoint.id, neighbor.id)
                ret.neighbourterms[neighbor.id] = -1/R
                ret.multiplier += 1/R
            
        #endloop
        print("Flow Equation: ", ret)
        return ret

    @staticmethod
    def constructType2Equation(enetwork, cpoint):
        ret = FlowEquation()
        ret.unknown = cpoint.id
        
        #go through the neighbours
        neighbors = enetwork.G.neighbors(cpoint.id)
        # print("neighbours of ", cpoint.id)

        for key in neighbors:
            neighbor = enetwork.getCPoint(key)

            if neighbor.pressure == None:
                R = enetwork.getResistanceBetween(cpoint.id, neighbor.id)
                ret.neighbourterms[neighbor.id] = -1/R
                ret.multiplier += 1/R
            else:
                R = enetwork.getResistanceBetween(cpoint.id, neighbor.id)
                ret.constantterm += neighbor.pressure/R
                ret.multiplier += 1/R


        print("Flow Equation: ", ret)
        return ret

    @staticmethod
    def constructType3Equation(enetwork, cpoint):
        ret = FlowEquation()
        ret.unknown = cpoint.id
        #go through the neighbours
        neighbors = enetwork.G.neighbors(cpoint.id)

        for key in neighbors:
            neighbor = enetwork.getCPoint(key)

            if neighbor.pressure == None:
                R = enetwork.getResistanceBetween(cpoint.id, neighbor.id)
                ret.neighbourterms[neighbor.id] = -1/R
                ret.multiplier += 1/R
            else:
                R = enetwork.getResistanceBetween(cpoint.id, neighbor.id)
                ret.constantterm += neighbor.pressure/R
                ret.multiplier += 1/R




        print("Flow Equation: ", ret)
        return ret


    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return str(self.__dict__)

