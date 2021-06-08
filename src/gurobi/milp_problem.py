# This module uses Gurobi optimizer

import gurobipy as gp
from gurobipy import GRB
import numpy as np
from task3.milpop import MILPOP


def solve(problem: MILPOP):
    """ Optimal problem """
    try:
        # Create a new model
        m = gp.Model("Optimal placement")
        print(len(problem.f.values))
        x = m.addMVar(shape=int(problem.f.size), lb=0.0, ub=GRB.INFINITY)
        # Set objective
        obj = problem.f.values
        m.setObjective(obj @ x, GRB.MAXIMIZE)

        m.addConstr(problem.ineq_array.values @ x <= problem.ineq_b, name="inequality")
        m.addConstr(problem.eq_array.values @ x == problem.eq_b, name="equality")
        # Optimize model
        m.optimize()

        print(x.X)

        print('Obj: %g' % m.objVal)

    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))

    except AttributeError:
        print('Encountered an attribute error')

    return m
