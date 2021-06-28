"""Mixed Integer Programming of Optimal Placement Problem """
import json


def get_mip_solution(solver: str ='gurobi'):
    with open('../input_data.json') as f:
        data = json.load(f)

    print(data['station']['position'])
    a =1
    pass

