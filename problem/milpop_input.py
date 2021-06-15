"""
Input of Mixed-integer linear programming optimization problem
We have set of station types and set of station places
We need to place stations minimizing the stations cost
"""
# gate = {'pos': {0: (7, 4)},
#         'lim': {0: float('inf')},
#         }
#
# obj = {'pos': {1: (1, 5),
#                2: (4.5, 4),
#                3: (6, 3),
#                4: (3.5, 5),
#                },
#        'lim': {1: 10,
#                2: 15,
#                3: 17,
#                4: 18,
#                }}
#
# sta = {'pos': {1: (2, 4),
#                2: (5, 5),
#                3: (2, 6),
#                4: (6, 5.5),
#                }}
#
# sta_type = {1: {'limit': 80, 'coverage': 1, 'link_distance': 6, 'cost': 70},
#             2: {'limit': 100, 'coverage': 2, 'link_distance': 5, 'cost': 75},
#             3: {'limit': 200, 'coverage': 3, 'link_distance': 6, 'cost': 85},
#             }


# gate = {'pos': {0: (8, 3)},
#         'lim': {0: float('inf')},
#         }
#
# obj = {'pos': {1: (1, 6),
#                2: (5, 6),
#                3: (8, 7),
#                4: (1, 3),
#                5: (2, 6),
#                6: (7, 5),
#                7: (4, 3),
#                8: (5, 2),
#                9: (4, 10),
#                10: (5, 9),
#                11: (1, 5),
#                12: (2, 3),
#                },
#        'lim': {1: 10,
#                2: 15,
#                3: 17,
#                4: 18,
#                5: 16,
#                6: 15,
#                7: 16,
#                8: 15,
#                9: 14,cd

#                10: 13,
#                11: 16,
#                12: 15,
#                }}
#
# sta = {'pos': {1: (4, 1),
#                2: (5, 4),
#                3: (4, 7),
#                4: (5, 8),
#                5: (0, 8),
#                6: (6, 8),
#                7: (0, 4),
#                8: (6, 10),
#                9: (12, 10),
#                10: (1, 7),
#                }}
#
# sta_type = {1: {'limit': 100, 'coverage': 3, 'link_distance': 5, 'cost': 75},
#             2: {'limit': 200, 'coverage': 4, 'link_distance': 6, 'cost': 85},
#             3: {'limit': 200, 'coverage': 4, 'link_distance': 6, 'cost': 95},
#             4: {'limit': 100, 'coverage': 4, 'link_distance': 7, 'cost': 105},
#             5: {'limit': 80, 'coverage': 2, 'link_distance': 5, 'cost': 60},
#             }



# gate = {'pos': {0: (8, 3)},
#         'lim': {0: float('inf')},
#         }
#
# obj = {'pos': {1: (1, 6),
#                2: (5, 6),
#                3: (8, 7),
#                4: (1, 3),
#                5: (2, 6),
#                6: (7, 5),
#                7: (4, 3),
#                8: (10, 3),
#                9: (4, 10),
#                10: (5, 9),
#                11: (1, 5),
#                12: (2, 3),
#                13: (2, 8),
#                14: (6, 2),
#                15: (10, 8),
#                16: (7, 8),
#                17: (10, 10),
#                18: (7, 9),
#                19: (6, 3),
#                20: (3, 8),
#                21: (10, 6),
#                22: (11, 8),
#                23: (1, 1),
#                24: (4, 2),
#                25: (0, 6),
#                26: (10, 4),
#                27: (4, 6),
#                28: (0, 1),
#                29: (12, 6),
#                30: (8, 11),
#                },
#        'lim': {1: 10,
#                2: 15,
#                3: 17,
#                4: 18,
#                5: 16,
#                6: 15,
#                7: 16,
#                8: 15,
#                9: 14,
#                10: 13,
#                11: 16,
#                12: 15,
#                13: 14,
#                14: 13,
#                15: 15,
#                16: 14,
#                17: 13,
#                18: 13,
#                19: 15,
#                20: 14,
#                21: 13,
#                22: 15,
#                23: 14,
#                24: 13,
#                25: 13,
#                26: 15,
#                27: 13,
#                28: 14,
#                29: 15,
#                30: 13,
#                }}
#
# sta = {'pos': {1: (4, 1),
#                2: (5, 4),
#                3: (4, 7),
#                4: (5, 8),
#                5: (0, 8),
#                6: (6, 8),
#                7: (0, 4),
#                8: (6, 10),
#                9: (12, 10),
#                10: (1, 7),
#                }}
#
# sta_type = {1: {'limit': 100, 'coverage': 6, 'link_distance': 5, 'cost': 75},
#             2: {'limit': 200, 'coverage': 5, 'link_distance': 6, 'cost': 85},
#             3: {'limit': 100, 'coverage': 6, 'link_distance': 6, 'cost': 95},
#             4: {'limit': 100, 'coverage': 6, 'link_distance': 7, 'cost': 105},
#             5: {'limit': 50, 'coverage': 5, 'link_distance': 6, 'cost': 60},
#             6: {'limit': 50, 'coverage': 5, 'link_distance': 6, 'cost': 70},
#             7: {'limit': 100, 'coverage': 6, 'link_distance': 7, 'cost': 50},
#             8: {'limit': 50, 'coverage': 4, 'link_distance': 6, 'cost': 55},
#             9: {'limit': 50, 'coverage': 7, 'link_distance': 7, 'cost': 110}
#             }





# gate = {'pos': {0: (8, 3)},
#         'lim': {0: float('inf')},
#         }
#
# obj = {'pos': {1: (1, 6),
#                2: (5, 6),
#                3: (8, 7),
#                4: (4, 3),
#                },
#        'lim': {1: 10,
#                2: 10,
#                3: 10,
#                4: 10,
#                }}
#
# sta = {'pos': {1: (4, 1),
#                2: (5, 4),
#                3: (4, 7),
#                }}
#
# sta_type = {1: {'limit': 100, 'coverage': 4, 'link_distance': 6, 'cost': 15},
#             2: {'limit': 100, 'coverage': 4.5, 'link_distance': 6, 'cost': 20},
#             }



gate = {'pos': {0: (8, 3)},
        'lim': {0: float('inf')},
        }

obj = {'pos': {1: (1, 6),
               2: (5, 6),
               3: (8, 7),
               4: (1, 3),
               5: (2, 6),
               6: (7, 5),
               7: (4, 3),
               8: (10, 3),
               9: (4, 10),
               10: (5, 9),
               11: (1, 5),
               12: (2, 3),
               13: (2, 8),
               14: (6, 2),
               15: (10, 8),
               16: (7, 8),
               17: (10, 10),
               18: (7, 9),
               19: (6, 3),
               20: (3, 8),
               },
       'lim': {1: 10,
               2: 15,
               3: 17,
               4: 18,
               5: 16,
               6: 15,
               7: 16,
               8: 15,
               9: 14,
               10: 13,
               11: 16,
               12: 15,
               13: 14,
               14: 13,
               15: 15,
               16: 14,
               17: 13,
               18: 13,
               19: 15,
               20: 14,
               }}

sta = {'pos': {1: (4, 1),
               2: (5, 4),
               3: (4, 7),
               4: (5, 8),
               5: (0, 8),
               6: (6, 8),
               7: (0, 4),
               8: (6, 10),
               9: (12, 10),
               10: (1, 7),
               }}

sta_type = {1: {'limit': 100, 'coverage': 6, 'link_distance': 5, 'cost': 75},
            2: {'limit': 200, 'coverage': 5, 'link_distance': 6, 'cost': 85},
            3: {'limit': 100, 'coverage': 6, 'link_distance': 6, 'cost': 95},
            4: {'limit': 100, 'coverage': 6, 'link_distance': 7, 'cost': 105},
            5: {'limit': 50, 'coverage': 5, 'link_distance': 6, 'cost': 60},
            6: {'limit': 50, 'coverage': 5, 'link_distance': 6, 'cost': 70},
            7: {'limit': 100, 'coverage': 6, 'link_distance': 7, 'cost': 70},
            8: {'limit': 50, 'coverage': 4, 'link_distance': 6, 'cost': 55},
            9: {'limit': 50, 'coverage': 7, 'link_distance': 7, 'cost': 110}
            }