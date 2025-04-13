# From https://github.com/damargulis/catan/
# Any modifications will be noted via comments and commits

SCREEN_SIZE = WIDTH, HEIGHT = 800, 640
BLACK = (0,0,0)
WHITE = (255,255,255)
SETTLEMENT_SIZE = 10
PORT_RADIUS = SETTLEMENT_SIZE * 2
CITY_SIZE = 20
ROAD_WIDTH = 10

DIALOG_HEIGHT = 50
TEXT_SIZE = 15
LINE_WIDTH = 5

ROBBER_SIZE = 10
ROBBER_COLOR = (0,0,0)

class Resource(object):
    BRICK = 0
    GRAIN = 1
    LUMBER = 2
    ORE = 3
    WOOL = 4

ResourceMap = [
        'Brick',
        'Grain',
        'Lumber',
        'Ore',
        'Wool',
]

ResourceColors = {
        Resource.BRICK: (128,0,0),
        Resource.LUMBER: (0,51,0),
        Resource.WOOL: (153,255,153),
        Resource.GRAIN: (255,204,0),
        Resource.ORE: (102,102,153),
        'desert': (153,102,0),
}

PlayerColors = {
        1: (255, 0, 0),
        2: (255, 255, 0),
        3: (0, 255, 0),
        4: (0, 0, 255)
}

PLAYER_WIDTH = 150
PLAYER_HEIGHT = 150

PLAYER_POSITIONS = [
        (0, 0, PLAYER_WIDTH, PLAYER_HEIGHT),
        (WIDTH - PLAYER_WIDTH, 0, PLAYER_WIDTH, PLAYER_HEIGHT),
        (0, HEIGHT - (PLAYER_HEIGHT + DIALOG_HEIGHT), PLAYER_WIDTH, PLAYER_HEIGHT),
        (WIDTH - PLAYER_WIDTH, HEIGHT - (PLAYER_HEIGHT + DIALOG_HEIGHT), PLAYER_WIDTH, PLAYER_HEIGHT),
]

CENTER = (420,295)
RESOURCE_RADIUS = 50

TilePositions = {
        0: (CENTER[0] - 2 * RESOURCE_RADIUS, CENTER[1] - 4 * RESOURCE_RADIUS),
        1: (CENTER[0], CENTER[1] - 4 * RESOURCE_RADIUS),
        2: (CENTER[0] + 2 * RESOURCE_RADIUS, CENTER[1] - 4 * RESOURCE_RADIUS),

        11: (CENTER[0] - 3 * RESOURCE_RADIUS, CENTER[1] - 2 * RESOURCE_RADIUS),
        12: (CENTER[0] - RESOURCE_RADIUS, CENTER[1] - 2 * RESOURCE_RADIUS),
        13: (CENTER[0] + RESOURCE_RADIUS, CENTER[1] - 2 * RESOURCE_RADIUS),
        3: (CENTER[0] + 3 * RESOURCE_RADIUS, CENTER[1] - 2 * RESOURCE_RADIUS),

        10: (CENTER[0] - 4 * RESOURCE_RADIUS, CENTER[1]),
        17: (CENTER[0] - 2 * RESOURCE_RADIUS, CENTER[1]),
        18: (CENTER[0], CENTER[1]),
        14: (CENTER[0] + 2 * RESOURCE_RADIUS, CENTER[1]),
        4: (CENTER[0] + 4 * RESOURCE_RADIUS, CENTER[1]),

        9: (CENTER[0] - 3 * RESOURCE_RADIUS, CENTER[1] + 2 * RESOURCE_RADIUS),
        16: (CENTER[0] - RESOURCE_RADIUS, CENTER[1] + 2 * RESOURCE_RADIUS),
        15: (CENTER[0] + RESOURCE_RADIUS, CENTER[1] + 2 * RESOURCE_RADIUS),
        5: (CENTER[0] + 3 * RESOURCE_RADIUS, CENTER[1] + 2 * RESOURCE_RADIUS),

        8: (CENTER[0] - 2 * RESOURCE_RADIUS, CENTER[1] + 4 * RESOURCE_RADIUS),
        7: (CENTER[0], CENTER[1] + 4 * RESOURCE_RADIUS),
        6: (CENTER[0] + 2 * RESOURCE_RADIUS, CENTER[1] + 4 * RESOURCE_RADIUS),
}

TileSettlementMap = {
        #Tile: [settlements]
        0: [0,1,2,8,9,10],
        1: [2,3,4,10,11,12],
        2: [4,5,6,12,13,14],

        11: [7,8,9,17,18,19],
        12: [9,10,11,19,20,21],
        13: [11,12,13,21,22,23],
        3: [13,14,15,23,24,25],

        10: [16,17,18,27,28,29],
        17: [18,19,20,29,30,31],
        18: [20,21,22,31,32,33],
        14: [22,23,24,33,34,35],
        4: [24,25,26,35,36,37],

        9: [28,29,30,38,39,40],
        16: [30,31,32,40,41,42],
        15: [32,33,34,42,43,44],
        5: [34,35,36,44,45,46],

        8: [39,40,41,47,48,49],
        7: [41,42,43,49,50,51],
        6: [43,44,45,51,52,53],
}

SettlementPositions = {
        0:  (CENTER[0] - 3 * RESOURCE_RADIUS, int(CENTER[1] - 4.75 * RESOURCE_RADIUS)),
        1:  (CENTER[0] - 2 * RESOURCE_RADIUS, int(CENTER[1] - 5.25 * RESOURCE_RADIUS)),
        2:  (CENTER[0] - 1 * RESOURCE_RADIUS, int(CENTER[1] - 4.75 * RESOURCE_RADIUS)),
        3:  (CENTER[0] + 0 * RESOURCE_RADIUS, int(CENTER[1] - 5.25 * RESOURCE_RADIUS)),
        4:  (CENTER[0] + 1 * RESOURCE_RADIUS, int(CENTER[1] - 4.75 * RESOURCE_RADIUS)),
        5:  (CENTER[0] + 2 * RESOURCE_RADIUS, int(CENTER[1] - 5.25 * RESOURCE_RADIUS)),
        6:  (CENTER[0] + 3 * RESOURCE_RADIUS, int(CENTER[1] - 4.75 * RESOURCE_RADIUS)),

        7:  (CENTER[0] - 4 * RESOURCE_RADIUS, int(CENTER[1] - 2.75 * RESOURCE_RADIUS)),
        8:  (CENTER[0] - 3 * RESOURCE_RADIUS, int(CENTER[1] - 3.25 * RESOURCE_RADIUS)),
        9:  (CENTER[0] - 2 * RESOURCE_RADIUS, int(CENTER[1] - 2.75 * RESOURCE_RADIUS)),
        10: (CENTER[0] - 1 * RESOURCE_RADIUS, int(CENTER[1] - 3.25 * RESOURCE_RADIUS)),
        11: (CENTER[0] + 0 * RESOURCE_RADIUS, int(CENTER[1] - 2.75 * RESOURCE_RADIUS)),
        12: (CENTER[0] + 1 * RESOURCE_RADIUS, int(CENTER[1] - 3.25 * RESOURCE_RADIUS)),
        13: (CENTER[0] + 2 * RESOURCE_RADIUS, int(CENTER[1] - 2.75 * RESOURCE_RADIUS)),
        14: (CENTER[0] + 3 * RESOURCE_RADIUS, int(CENTER[1] - 3.25 * RESOURCE_RADIUS)),
        15: (CENTER[0] + 4 * RESOURCE_RADIUS, int(CENTER[1] - 2.75 * RESOURCE_RADIUS)),

        16: (CENTER[0] - 5 * RESOURCE_RADIUS, int(CENTER[1] - 0.75 * RESOURCE_RADIUS)),
        17: (CENTER[0] - 4 * RESOURCE_RADIUS, int(CENTER[1] - 1.25 * RESOURCE_RADIUS)),
        18: (CENTER[0] - 3 * RESOURCE_RADIUS, int(CENTER[1] - 0.75 * RESOURCE_RADIUS)),
        19: (CENTER[0] - 2 * RESOURCE_RADIUS, int(CENTER[1] - 1.25 * RESOURCE_RADIUS)),
        20: (CENTER[0] - 1 * RESOURCE_RADIUS, int(CENTER[1] - 0.75 * RESOURCE_RADIUS)),
        21: (CENTER[0] + 0 * RESOURCE_RADIUS, int(CENTER[1] - 1.25 * RESOURCE_RADIUS)),
        22: (CENTER[0] + 1 * RESOURCE_RADIUS, int(CENTER[1] - 0.75 * RESOURCE_RADIUS)),
        23: (CENTER[0] + 2 * RESOURCE_RADIUS, int(CENTER[1] - 1.25 * RESOURCE_RADIUS)),
        24: (CENTER[0] + 3 * RESOURCE_RADIUS, int(CENTER[1] - 0.75 * RESOURCE_RADIUS)),
        25: (CENTER[0] + 4 * RESOURCE_RADIUS, int(CENTER[1] - 1.25 * RESOURCE_RADIUS)),
        26: (CENTER[0] + 5 * RESOURCE_RADIUS, int(CENTER[1] - 0.75 * RESOURCE_RADIUS)),

        27: (CENTER[0] - 5 * RESOURCE_RADIUS, int(CENTER[1] + 0.75 * RESOURCE_RADIUS)),
        28: (CENTER[0] - 4 * RESOURCE_RADIUS, int(CENTER[1] + 1.25 * RESOURCE_RADIUS)),
        29: (CENTER[0] - 3 * RESOURCE_RADIUS, int(CENTER[1] + 0.75 * RESOURCE_RADIUS)),
        30: (CENTER[0] - 2 * RESOURCE_RADIUS, int(CENTER[1] + 1.25 * RESOURCE_RADIUS)),
        31: (CENTER[0] - 1 * RESOURCE_RADIUS, int(CENTER[1] + 0.75 * RESOURCE_RADIUS)),
        32: (CENTER[0] + 0 * RESOURCE_RADIUS, int(CENTER[1] + 1.25 * RESOURCE_RADIUS)),
        33: (CENTER[0] + 1 * RESOURCE_RADIUS, int(CENTER[1] + 0.75 * RESOURCE_RADIUS)),
        34: (CENTER[0] + 2 * RESOURCE_RADIUS, int(CENTER[1] + 1.25 * RESOURCE_RADIUS)),
        35: (CENTER[0] + 3 * RESOURCE_RADIUS, int(CENTER[1] + 0.75 * RESOURCE_RADIUS)),
        36: (CENTER[0] + 4 * RESOURCE_RADIUS, int(CENTER[1] + 1.25 * RESOURCE_RADIUS)),
        37: (CENTER[0] + 5 * RESOURCE_RADIUS, int(CENTER[1] + 0.75 * RESOURCE_RADIUS)),

        38: (CENTER[0] - 4 * RESOURCE_RADIUS, int(CENTER[1] + 2.75 * RESOURCE_RADIUS)),
        39: (CENTER[0] - 3 * RESOURCE_RADIUS, int(CENTER[1] + 3.25 * RESOURCE_RADIUS)),
        40: (CENTER[0] - 2 * RESOURCE_RADIUS, int(CENTER[1] + 2.75 * RESOURCE_RADIUS)),
        41: (CENTER[0] - 1 * RESOURCE_RADIUS, int(CENTER[1] + 3.25 * RESOURCE_RADIUS)),
        42: (CENTER[0] + 0 * RESOURCE_RADIUS, int(CENTER[1] + 2.75 * RESOURCE_RADIUS)),
        43: (CENTER[0] + 1 * RESOURCE_RADIUS, int(CENTER[1] + 3.25 * RESOURCE_RADIUS)),
        44: (CENTER[0] + 2 * RESOURCE_RADIUS, int(CENTER[1] + 2.75 * RESOURCE_RADIUS)),
        45: (CENTER[0] + 3 * RESOURCE_RADIUS, int(CENTER[1] + 3.25 * RESOURCE_RADIUS)),
        46: (CENTER[0] + 4 * RESOURCE_RADIUS, int(CENTER[1] + 2.75 * RESOURCE_RADIUS)),

        47: (CENTER[0] - 3 * RESOURCE_RADIUS, int(CENTER[1] + 4.75 * RESOURCE_RADIUS)),
        48: (CENTER[0] - 2 * RESOURCE_RADIUS, int(CENTER[1] + 5.25 * RESOURCE_RADIUS)),
        49: (CENTER[0] - 1 * RESOURCE_RADIUS, int(CENTER[1] + 4.75 * RESOURCE_RADIUS)),
        50: (CENTER[0] + 0 * RESOURCE_RADIUS, int(CENTER[1] + 5.25 * RESOURCE_RADIUS)),
        51: (CENTER[0] + 1 * RESOURCE_RADIUS, int(CENTER[1] + 4.75 * RESOURCE_RADIUS)),
        52: (CENTER[0] + 2 * RESOURCE_RADIUS, int(CENTER[1] + 5.25 * RESOURCE_RADIUS)),
        53: (CENTER[0] + 3 * RESOURCE_RADIUS, int(CENTER[1] + 4.75 * RESOURCE_RADIUS)),
}

Roads = [
        (0,1),
        (1,2),
        (2,3),
        (3,4),
        (4,5),
        (5,6),

        (7,8),
        (8,9),
        (9,10),
        (10,11),
        (11,12),
        (12,13),
        (13,14),
        (14,15),

        (16,17),
        (17,18),
        (18,19),
        (19,20),
        (20,21),
        (21,22),
        (22,23),
        (23,24),
        (24,25),
        (25,26),

        (27,28),
        (28,29),
        (29,30),
        (30,31),
        (31,32),
        (32,33),
        (33,34),
        (34,35),
        (35,36),
        (36,37),

        (38,39),
        (39,40),
        (40,41),
        (41,42),
        (42,43),
        (43,44),
        (44,45),
        (45,46),

        (47,48),
        (48,49),
        (49,50),
        (50,51),
        (51,52),
        (52,53),

        (0,8),
        (2,10),
        (4,12),
        (6,14),

        (7,17),
        (9,19),
        (11,21),
        (13,23),
        (15,25),

        (16,27),
        (18,29),
        (20,31),
        (22,33),
        (24,35),
        (26,37),

        (28,38),
        (30,40),
        (32,42),
        (34,44),
        (36,46),

        (39,47),
        (41,49),
        (43,51),
        (45,53),
]

def get_midpoint(point1, point2):
    return ((point1[0] + point2[0]) * .5, (point1[1] + point2[1]) * .5)

RoadMidpoints = {
        i: get_midpoint(SettlementPositions[road[0]], SettlementPositions[road[1]])
        for i,road in enumerate(Roads)
}

Costs = {
        'road': {
            Resource.BRICK: 1,
            Resource.LUMBER: 1,
        },
        'settlement': {
            Resource.BRICK: 1,
            Resource.GRAIN: 1,
            Resource.LUMBER: 1,
            Resource.WOOL: 1,
        },
        'city': {
            Resource.GRAIN: 2,
            Resource.ORE: 3,
        },
        'd_card': {
            Resource.GRAIN: 1,
            Resource.ORE: 1,
            Resource.WOOL: 1,
        },
}

Ports = {
        2: (Resource.LUMBER, 2),
        3: (Resource.LUMBER, 2),
        5: ('any', 3),
        6: ('any', 3),
        7: (Resource.BRICK, 2),
        8: (Resource.BRICK, 2),
        15: (Resource.GRAIN, 2),
        16: ('any', 3),
        25: (Resource.GRAIN, 2),
        27: ('any', 3),
        36: (Resource.ORE, 2),
        38: ('any', 3),
        39: ('any', 3),
        46: (Resource.ORE, 2),
        49: (Resource.WOOL, 2),
        50: (Resource.WOOL, 2),
        52: ('any', 3),
        53: ('any', 3),
}
