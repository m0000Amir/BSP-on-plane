"""
Solution task 1
We have set of placed stations
We need to check network existence admissibility
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

sta_set = {1: {'limit': 200, 'coverage': 10, 'link_distance': 10},
           }

