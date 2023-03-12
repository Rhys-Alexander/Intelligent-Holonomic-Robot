import sys
import math
import cv2
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString, Polygon

# y,x
BOARD_DIMENSIONS = (3000, 2000)

# Colours, RGB
RED = (255, 0, 0)
GREEN = (0, 170, 18)
BLUE = (0, 92, 230)
PINK = (195, 0, 195)
YELLOW = (255, 191, 0)
BROWN = (46, 15, 23)
GRAY = (173, 184, 153)

# Thicknesses
BOARD_THICKNESS = 10
ITEM_THICKNESS = 15
BOT_THICKNESS = 20
GRAPH_THICKNESS = 2

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

# Blank board
board = 255 * np.ones(shape=[*BOARD_DIMENSIONS, 3], dtype=np.uint8)
# Img board
# board = cv2.imread("pics/orthogonal_board.png")


def drawBox(pt, colour, radius_modifier=0):
    p1, p2 = pt
    if radius_modifier:
        p1 = (p1[0] - radius_modifier, p1[1] - radius_modifier)
        p2 = (p2[0] + radius_modifier, p2[1] + radius_modifier)
    cv2.rectangle(
        board,
        pt1=p1,
        pt2=p2,
        color=colour,
        thickness=BOARD_THICKNESS,
    )


def drawPuck(board, pt, colour):
    x, y = pt
    cv2.circle(
        board,
        center=(x, y),
        radius=PUCK_RADIUS,
        color=colour,
        thickness=ITEM_THICKNESS,
    )


def drawCherry(board, pt):
    x, y = pt
    cv2.circle(
        board,
        center=(x, y),
        radius=10,
        color=RED,
        thickness=ITEM_THICKNESS,
    )


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


# Board Setup
for start, colour in ((BLUE_START, BLUE), (GREEN_START, GREEN)):
    x, y = start
    drawBox(start, colour)
    drawBox(start, colour, radius_modifier=-50)

for plate in BLUE_PLATES:
    drawBox(plate, BLUE)

for plate in GREEN_PLATES:
    drawBox(plate, GREEN)

for holder in CHERRY_HOLDERS:
    drawBox(holder, GRAY)

blank_state = board.copy()

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
team_colour = BLUE
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "green":
            team_colour = GREEN
        elif sys.argv[1] == "blue":
            team_colour = BLUE
        else:
            print("Invalid argument, use green or blue")
            exit()
    else:
        print("No argument given, defaulting to blue")


def getItems(team_colour):
    all_pucks = pink_pucks + yellow_pucks + brown_pucks
    if team_colour == BLUE:
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


items = getItems(team_colour)

# To Refresh the board
def drawRefresh(board):
    board = blank_state.copy()
    for pucks, colour in zip(
        (pink_pucks, yellow_pucks, brown_pucks), (PINK, YELLOW, BROWN)
    ):
        for puck in pucks:
            drawPuck(board, puck, colour)

    for cherry in cherries:
        drawCherry(board, cherry)

    for bot, colour in ((blue_bot, BLUE), (green_bot, GREEN)):
        x, y, rot = bot
        cv2.circle(
            board,
            center=(x, y),
            radius=BOT_RADIUS,
            color=colour,
            thickness=BOT_THICKNESS,
        )
        cv2.line(
            board,
            pt1=(x, y),
            pt2=(
                math.ceil(x + BOT_RADIUS * np.cos(np.radians(rot))),
                math.ceil(y + BOT_RADIUS * np.sin(np.radians(rot))),
            ),
            color=colour,
            thickness=BOT_THICKNESS,
        )
    return board


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


def drawGraph(board, graph, nodes):
    for i, row in enumerate(graph):
        for j, val in enumerate(row[i + 1 :]):
            if val:
                cv2.line(
                    board,
                    pt1=nodes[i],
                    pt2=nodes[i + 1 + j],
                    color=team_colour,
                    thickness=GRAPH_THICKNESS,
                )
    return board


# TODO refreshState()
board = drawRefresh(board)
graph = makeGraph(items)
board = drawGraph(board, graph, items)

plt.imshow(board)
plt.show()
