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


def getFreeAndCaptivePucks(all_pucks, plates):
    captive_pucks = []
    for puck in all_pucks:
        for plate in plates:
            p1x, p1y = plate[0]
            p2x, p2y = plate[1]
            if p1x <= puck[0] <= p2x and p1y <= puck[1] <= p2y:
                captive_pucks.append(puck)
    free_pucks = [puck for puck in all_pucks if puck not in captive_pucks]
    return free_pucks, captive_pucks


def checkCollision(line_ends, obstacle, radius):
    margin = BOT_RADIUS + radius
    obstacle = Point(*obstacle)
    line = LineString(line_ends)
    if line.distance(obstacle) <= margin:
        return True


# 3 length list, x pos, y pos, and rotation
blue_bot = [225, 225, 90]
green_bot = [1775, 225, 90]
green_bot = [1000, 1500, 90]

# lists of tuples, x pos, y pos
pink_pucks = [(225, 575), (1775, 575), (225, 2425), (1775, 2425)] * 3
yellow_pucks = [(225, 775), (1775, 775), (225, 2225), (1775, 2225)] * 3
brown_pucks = [(725, 1125), (1275, 1125), (725, 1875), (1275, 1875)] * 3

# cherry setup
cherries = []
for cherry_holder in CHERRY_HOLDERS:
    x1, y1 = cherry_holder[0]
    for i in range(10):
        cherries.append(
            (x1 + CHERRY_RADIUS, y1 + CHERRY_RADIUS + i * CHERRY_RADIUS * 2)
        )

# team items
blueTeam = True
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


def getItems(blueTeam):
    all_pucks = pink_pucks + yellow_pucks + brown_pucks
    if blueTeam:
        items = (
            getFreeAndCaptivePucks(all_pucks, BLUE_PLATES)[0]
            + [blue_bot[:2]]
            + BLUE_PLATE_CENTRES
        )
    else:
        items = (
            getFreeAndCaptivePucks(all_pucks, GREEN_PLATES)[0]
            + [green_bot[:2]]
            + GREEN_PLATE_CENTRES
        )
    return items


items = getItems(blueTeam)


def makeGraph(nodes):
    graph = np.zeros((len(nodes), len(nodes)))
    for i, item in enumerate(nodes[:-4]):
        for j, item2 in enumerate(nodes[i + 1 :]):
            # graph[i, j + i + 1] = graph[j + i + 1, i] = math.dist(item, item2) + 1
            if not checkCollision([item, item2], green_bot[:2], BOT_RADIUS):
                graph[i, j + i + 1] = math.dist(item, item2) + 1
            if not checkCollision([item2, item], green_bot[:2], BOT_RADIUS):
                graph[j + i + 1, i] = math.dist(item, item2) + 1
    return graph


# TODO refreshState()
board = vis.Board()
board.drawRefresh(pink_pucks, yellow_pucks, brown_pucks, cherries, blue_bot, green_bot)
graph = makeGraph(items)
board.drawGraph(graph, items)
board.display()
