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
        # print(len(problem.upper_bounds[problem.upper_bounds == 1]))
        # print(len(problem.upper_bounds[problem.upper_bounds == float('Inf')]))
        column_name = problem.f.columns.str.startswith('z').sum()
        zvar_count = problem.f.columns.str.startswith('z').sum()
        xvar_count = problem.f.columns.str.startswith('x').sum()
        yvar_count = problem.f.columns.str.startswith('y').sum()
        vtype = ([GRB.BINARY] * zvar_count +
                 [GRB.CONTINUOUS] * xvar_count +
                 [GRB.BINARY] * yvar_count)
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
        x = m.addMVar(shape=int(problem.f.size),
                      lb=0.0, ub=problem.upper_bounds,
                      vtype=vtype)
        # Set objective
        obj = problem.f.values

        m.setObjective(obj @ x, GRB.MINIMIZE)

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

    return x.X
