import cv2
import math
import numpy as np
import matplotlib.pyplot as plt


# Colours, RGB
RED = (255, 0, 0)
GREEN = (0, 170, 18)
BLUE = (0, 92, 230)
PINK = (195, 0, 195)
YELLOW = (255, 191, 0)
BROWN = (46, 15, 23)
GRAY = (173, 184, 153)

# Integer Radiuses
PUCK_RADIUS = 60
PLATE_RADIUS = 225
BOT_RADIUS = 200
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

# 3 length tuple, x pos, y pos, and rotation
blue_bot = (225, 225, 90)
green_bot = (1775, 225, 90)

# lists of tuples, x pos, y pos
pink_pucks = [(225, 575), (1775, 575), (225, 2425), (1775, 2425)]
yellow_pucks = [(225, 775), (1775, 775), (225, 2225), (1775, 2225)]
brown_pucks = [(725, 1125), (1275, 1125), (725, 1875), (1275, 1875)]
puck_colours = ((pink_pucks, PINK), (yellow_pucks, YELLOW), (brown_pucks, BROWN))

# cherry setup
cherries = []
for cherry_holder in CHERRY_HOLDERS:
    x1, y1 = cherry_holder[0]
    for i in range(10):
        cherries.append((x1 + 15, y1 + 15 + i * 30))

# team items
blue_items = (
    pink_pucks + yellow_pucks + brown_pucks + [blue_bot[:2]] + BLUE_PLATE_CENTRES
)
green_items = (
    pink_pucks + yellow_pucks + brown_pucks + [green_bot[:2]] + GREEN_PLATE_CENTRES
)

# Blank board
board = 255 * np.ones(shape=[3000, 2000, 3], dtype=np.uint8)
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
        thickness=10,
    )


def drawPuck(board, pt, color):
    x, y = pt
    cv2.circle(
        board,
        center=(x, y),
        radius=PUCK_RADIUS,
        color=color,
        thickness=10,
    )


def drawCherry(board, pt):
    x, y = pt
    cv2.circle(
        board,
        center=(x, y),
        radius=10,
        color=RED,
        thickness=10,
    )


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

start_state = board.copy()

# To Refresh the board
def refresh(board):
    board = start_state.copy()
    for pucks, colour in puck_colours:
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
            thickness=20,
        )
        cv2.line(
            board,
            pt1=(x, y),
            pt2=(
                math.ceil(x + 150 * np.cos(np.radians(rot))),
                math.ceil(y + 150 * np.sin(np.radians(rot))),
            ),
            color=colour,
            thickness=40,
        )
    return board


def makeGraph(board):
    for item in blue_items:
        for item2 in blue_items:
            if item != item2:
                cv2.line(
                    board,
                    pt1=item,
                    pt2=item2,
                    color=BLUE,
                    thickness=3,
                )
    for item in green_items:
        for item2 in green_items:
            if item != item2:
                cv2.line(
                    board,
                    pt1=item,
                    pt2=item2,
                    color=GREEN,
                    thickness=3,
                )
    return board


board = refresh(board)
board = makeGraph(board)
plt.imshow(board)

plt.show()
