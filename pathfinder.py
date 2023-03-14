import sys
import math
import visualiser as vis

import numpy as np
from shapely.geometry import Point, LineString, Polygon

# Integer Radiuses
PUCK_RADIUS = 60
PLATE_RADIUS = 225
BOT_RADIUS = 200
CHERRY_RADIUS = 15
# 2 length tuple, x pos and y pos
BLUE_START_CENTRE = (225, 225)
BLUE_START = ((0, 0), (450, 450))
GREEN_START_CENTRE = (1775, 225)
GREEN_START = ((1550, 0), (2000, 450))
# list of 2 length tuple, x pos and y pos
BLUE_PLATE_CENTRES = [(1775, 1125), (225, 1875), (725, 2775), (1775, 2775)]
GREEN_PLATE_CENTRES = [(225, 1125), (1775, 1875), (225, 2775), (1275, 2775)]
# lists of 2 length tuple, top left and bottom right
BLUE_PLATES = [
    ((1550, 900), (2000, 1350)),
    ((0, 1650), (450, 2100)),
    ((500, 2550), (950, 3000)),
    ((1550, 2550), (2000, 3000)),
]
GREEN_PLATES = [
    ((0, 900), (450, 1350)),
    ((1550, 1650), (2000, 2100)),
    ((0, 2550), (450, 3000)),
    ((1050, 2550), (1500, 3000)),
]
CHERRY_HOLDERS = [
    ((985, 0), (1015, 300)),
    ((985, 2700), (1015, 3000)),
    ((0, 1350), (30, 1650)),
    ((1970, 1350), (2000, 1650)),
]
MAX_CAPACITY = 18
ENEMY_BOT_WEIGHT = 10**8


class PathFinder:
    def __init__(self, blueTeam):
        self.capacity = MAX_CAPACITY
        self.start = BLUE_START_CENTRE if blueTeam else GREEN_START_CENTRE
        self.enemy_start = GREEN_START if blueTeam else BLUE_START
        self.PLATE_CENTRES = BLUE_PLATE_CENTRES if blueTeam else GREEN_PLATE_CENTRES
        self.plates = BLUE_PLATES if blueTeam else GREEN_PLATES
        self.cherry_holders = CHERRY_HOLDERS
        self.blueTeam = blueTeam
        # tuple, x pos, y pos, rotation
        self.bot = (225, 225, 90) if blueTeam else (1775, 225, 90)
        self.enemy_bot = (1775, 225, 90) if blueTeam else (225, 225, 90)
        # lists of tuples, x pos, y pos
        self.pink_pucks = [(225, 575), (1775, 575), (225, 2425), (1775, 2425)] * 3
        self.yellow_pucks = [(225, 775), (1775, 775), (225, 2225), (1775, 2225)] * 3
        self.brown_pucks = [(725, 1125), (1275, 1125), (725, 1875), (1275, 1875)] * 3
        self.cherries = []
        for cherry_holder in CHERRY_HOLDERS:
            x1, y1 = cherry_holder[0]
            for i in range(10):
                self.cherries.append(
                    (x1 + CHERRY_RADIUS, y1 + CHERRY_RADIUS + i * CHERRY_RADIUS * 2)
                )
        # self.randomise()
        self.setItems()
        self.makeGraph()
        self.setPath()

    def randomise(self):
        import random

        self.pink_pucks = [
            (random.randint(200, 2000), random.randint(200, 3000))
            for _ in self.pink_pucks
        ]
        self.yellow_pucks = [
            (random.randint(200, 2000), random.randint(200, 3000))
            for _ in self.yellow_pucks
        ]
        self.brown_pucks = [
            (random.randint(200, 2000), random.randint(200, 3000))
            for _ in self.brown_pucks
        ]
        self.enemy_bot = (
            random.randint(200, 2000),
            random.randint(200, 3000),
            random.randint(0, 360),
        )
        self.bot = (
            random.randint(200, 2000),
            random.randint(200, 3000),
            random.randint(0, 360),
        )

    def setItems(self):
        self.all_pucks = self.pink_pucks + self.yellow_pucks + self.brown_pucks
        captive_pucks = []
        for puck in self.all_pucks:
            for plate in self.plates + [self.enemy_start]:
                p1x, p1y = plate[0]
                p2x, p2y = plate[1]
                if p1x <= puck[0] <= p2x and p1y <= puck[1] <= p2y:
                    captive_pucks.append(puck)
        free_pucks = [puck for puck in self.all_pucks if puck not in captive_pucks]
        self.free_pucks = free_pucks
        self.captive_pucks = captive_pucks
        self.items = self.free_pucks + self.PLATE_CENTRES + [self.bot[:2]]

    def checkCollision(self, line_ends, obstacle, radius):
        margin = BOT_RADIUS + radius
        obstacle = Point(*obstacle)
        line = LineString(line_ends)
        if line.distance(obstacle) <= margin:
            return True

    def checkCollisions(self, line_ends):
        if self.checkCollision(line_ends, self.enemy_bot, BOT_RADIUS):
            return True
        for holder in self.cherry_holders:
            x1, y1 = holder[0]
            x2, y2 = holder[1]
            if (
                Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)]).distance(
                    LineString(line_ends)
                )
                <= BOT_RADIUS
            ):
                return True

    def makeGraph(self):
        graph = np.zeros((len(self.items), len(self.items)))
        for i, item in enumerate(self.items[: -(len(self.PLATE_CENTRES) + 1)]):
            for j, item2 in enumerate(self.items[i + 1 :]):
                # Put in graph if no collisions with weight of distance plus inverse square of distance to enemy bot
                if not self.checkCollisions([item, item2]):
                    graph[i, j + i + 1] = graph[j + i + 1, i] = (
                        math.dist(item, item2)
                        + 1
                        + ENEMY_BOT_WEIGHT
                        * 1
                        / (
                            (LineString([item, item2]).distance(Point(self.enemy_bot)))
                            ** 2
                        )
                    )
        self.graph = graph

    def displayGraph(self):
        board = vis.Board()
        board.drawItems(
            self.pink_pucks,
            self.yellow_pucks,
            self.brown_pucks,
            self.cherries,
            self.bot,
            self.enemy_bot,
        )
        board.drawGraph(self.graph, self.items)
        board.drawPath(self.path)
        board.display()

    def getGreedyPath(self):
        max_depth = min(self.capacity, len(self.free_pucks))
        path = [len(self.items) - 1]
        next = -1
        for _ in range(max_depth):
            edges = self.graph[next][: -(len(self.PLATE_CENTRES) + 1)]
            pairs = {
                j: node for j, node in enumerate(edges) if not j in path and node != 0
            }
            next = min(pairs, key=pairs.get)
            path.append(next)
        edges = self.graph[next][-(len(self.PLATE_CENTRES) + 1) : -1]
        pairs = {j: node for j, node in enumerate(edges) if not j in path and node != 0}
        next = min(pairs, key=pairs.get)
        path.append(next + len(self.items) - (len(self.PLATE_CENTRES) + 1))
        path = [self.items[i] for i in path]
        return path

    def setPath(self):
        self.path = self.getGreedyPath()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "green":
            blueTeam = False
        elif sys.argv[1] == "blue":
            blueTeam = True
        else:
            print("Invalid argument, use green or blue")
            exit()
    else:
        print("No argument given, defaulting to blue")
        blueTeam = True

    pf = PathFinder(blueTeam)
    pf.displayGraph()
