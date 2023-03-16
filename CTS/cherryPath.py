import sys
import math
import visualiser as vis

import numpy as np
from shapely.geometry import Point, LineString, Polygon

CHERRY_RADIUS = 15
CHERRY_HOLDERS = [
    ((985, 0), (1015, 300)),
    ((985, 2700), (1015, 3000)),
    ((0, 1350), (30, 1650)),
    ((1970, 1350), (2000, 1650)),
]
BOT_RADIUS = 200
# 2 length tuple, x pos and y pos
BLUE_START_CENTRE = (225, 225)
BLUE_START = ((0, 0), (450, 450))
GREEN_START_CENTRE = (1775, 225)
GREEN_START = ((1550, 0), (2000, 450))
ENEMY_BOT_WEIGHT = 10**8.5

# FIXME not efficient and simple enough for the secondary robot
# TODO make cherry paths more accessible, different algorithm, A*?


class PathFinder:
    def __init__(self, blueTeam):
        self.start = BLUE_START_CENTRE if blueTeam else GREEN_START_CENTRE
        self.enemy_start = GREEN_START if blueTeam else BLUE_START
        self.blueTeam = blueTeam
        # tuple, x pos, y pos, rotation
        self.bot = (225, 225, 90) if blueTeam else (1775, 225, 90)
        self.enemy_bot = (1775, 225, 90) if blueTeam else (225, 225, 90)
        # lists of tuples, x pos, y pos
        self.cherries = [
            (1000, BOT_RADIUS),
            (1000, 3000 - BOT_RADIUS),
            (15, 1500),
            (1985, 1500),
        ]
        self.randomise()
        self.setItems()
        self.makeGraph()
        self.setPath()

    def randomise(self):
        import random

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
        cherry_collects = []
        for x, y in self.cherries:
            pt1 = (x - BOT_RADIUS - CHERRY_RADIUS * 2, y)
            pt2 = (x + BOT_RADIUS + CHERRY_RADIUS * 2, y)
            if 0 <= pt1[0] <= 2000:
                cherry_collects.append(pt1)
            if 0 <= pt2[0] <= 2000:
                cherry_collects.append(pt2)
        self.cherry_collects = cherry_collects
        self.items = self.cherry_collects + [self.bot[:2]]

    def checkCollision(self, line_ends, obstacle, radius):
        margin = BOT_RADIUS + radius
        obstacle = Point(*obstacle)
        line = LineString(line_ends)
        if line.distance(obstacle) <= margin:
            return True

    def checkCollisions(self, line_ends):
        margin = BOT_RADIUS * 2
        obstacle = Point(*self.enemy_bot[:2])
        line = LineString(line_ends)
        if line.distance(obstacle) <= margin:
            return True
        for holder in CHERRY_HOLDERS:
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
        for i, item in enumerate(self.items[:-1]):
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
            self.bot,
            self.enemy_bot,
            cherries=self.cherries,
        )
        board.drawGraph(self.graph, self.items)
        board.drawPath(self.path)
        board.display()

    def getGreedyPath(self):
        path = [len(self.items) - 1]
        next = -1
        while True:
            edges = self.graph[next][:-1]
            pairs = {
                j: node for j, node in enumerate(edges) if not j in path and node != 0
            }
            try:
                next = min(pairs, key=pairs.get)
                path.append(next)
            except ValueError:
                print("No max path found")
                break
        return [self.items[i] for i in path]

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

while True:
    pf = PathFinder(blueTeam)
    pf.displayGraph()
