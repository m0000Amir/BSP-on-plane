"""
Input of Mixed-integer Linear programming problem feasible solution
We have set of stations and set of station places
We need to place stations and check network existence admissibility
"""
gate = {'pos': {0: (8, 3)},
        'lim': {0: float('inf')},
        }

obj = {'pos': {1: (1, 6),
               2: (5, 6),
               3: (8, 7),
               4: (4, 3),
               },
       'lim': {1: 10,
               2: 10,
               3: 10,
               4: 10,
               }}

sta = {'pos': {1: (4, 1),
               2: (5, 4),
               3: (4, 7),
               }}

sta_set = {1: {'limit': 100, 'coverage': 4, 'link_distance': 6},
           2: {'limit': 100, 'coverage': 5, 'link_distance': 6},
           }

