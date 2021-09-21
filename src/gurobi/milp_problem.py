# This module uses Gurobi optimizer

import gurobipy as gp
from gurobipy import GRB
import numpy as np
# from task3.milpop import MILPOP
from src.mipop.mipop import MIP


def solve(problem: MIP):
    """ Optimal problem """
    try:
        # Create a new model
        m = gp.Model("Optimal placement")
        # print(len(problem.upper_bounds[problem.upper_bounds == 1]))
        # print(len(problem.upper_bounds[problem.upper_bounds == float('Inf')]))
        xvar_count = len(problem.of.upper_bounds[problem.of.upper_bounds == float('Inf')])
        yvar_count = len(problem.of.upper_bounds[problem.of.upper_bounds == 1])
        vtype = [GRB.CONTINUOUS] * xvar_count + [GRB.BINARY] * yvar_count
        # x = m.addMVar(shape=xvar_count,
        #               lb=0,
        #               ub=GRB.INFINITY,
        #               vtype=GRB.CONTINUOUS,
        #               name='x')
        # y = m.addMVar(shape=yvar_count,
        #               lb=0,
        #               ub=1,
        #               vtype=GRB.BINARY,
        #               name='y')
        # aa = [GRB.INFINITY]
        x = m.addMVar(shape=int(problem.of.data.size),
                      lb=0.0, ub=problem.of.upper_bounds,
                      vtype=vtype)
        # Set objective
        obj = problem.of.data.values

        m.setObjective(obj @ x, GRB.MINIMIZE)

        m.addConstr(problem.ineq_constraints.data.values @ x <= problem.ineq_constraints.b, name="inequality")
        m.addConstr(problem.eq_constraints.data.values @ x == problem.eq_constraints.b, name="equality")
        # Optimize model
        m.optimize()

        print(x.X)

        print('Obj: %g' % m.objVal)

    except gp.GurobiError as e:
        print('Error code ' + str(e.errno) + ": " + str(e))

    except AttributeError:
        print('Encountered an attribute error')

    return x.X
