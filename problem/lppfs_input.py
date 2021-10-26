"""
Solution task 1
We have set of placed stations
We need to check network existence admissibility
"""
gate = {'pos': {0: (8, 15)},
        'lim': {0: float('inf')},
        }

obj = {'pos': {1: (2, 6),
               2: (14, 6),
               3: (10, 15),
               4: (11, 4),
               5: (3.2, 2.1),
               },
       'lim': {1: 11,
               2: 12,
               3: 13,
               4: 14,
               5: 15,
               }}

sta = {'pos': {1: (2, 4),
               2: (10, 10)
               }}

sta_set = {1: {'limit': 130, 'coverage': 100, 'link_distance': 100},
           }

