import cv2
import math
import numpy as np
import matplotlib.pyplot as plt


# Colours
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
BLUE_START = (225, 225)
GREEN_START = (1775, 225)
BLUE_PLATES = [(1775, 1125), (225, 1875), (725, 2775), (1775, 2775)]
GREEN_PLATES = [(225, 1125), (1775, 1875), (225, 2775), (1275, 2775)]
# list of top left corners, 30 wide, 300 long
CHERRY_HOLDERS = [(985, 0), (985, 2700), (0, 1350), (1970, 1350)]

# 3 length tuple, x pos, y pos, and rotation
blue_bot = (225, 225, 90)
green_bot = (1775, 225, 90)

# lists of tuples, x pos, y pos
pink_pucks = [(225, 575), (1775, 575), (225, 2425), (1775, 2425)]
yellow_pucks = [(225, 775), (1775, 775), (225, 2225), (1775, 2225)]
brown_pucks = [(725, 1125), (1275, 1125), (725, 1875), (1275, 1875)]
puck_list = ((pink_pucks, PINK), (yellow_pucks, YELLOW), (brown_pucks, BROWN))
cherries = []

# Blank board
board = 255 * np.ones(shape=[3000, 2000, 3], dtype=np.uint8)
# Img board
# board = cv2.imread("pics/orthogonal_board.png")


def drawBox(pt, color, radius=PLATE_RADIUS):
    x, y = pt
    cv2.rectangle(
        board,
        pt1=(x - radius, y - radius),
        pt2=(x + radius, y + radius),
        color=color,
        thickness=10,
    )


def drawCherryBox(pt):
    x, y = pt
    cv2.rectangle(
        board,
        pt1=(x, y),
        pt2=(x + 30, y + 300),
        color=GRAY,
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


# Board Setup
for start, colour in ((BLUE_START, BLUE), (GREEN_START, GREEN)):
    x, y = start
    drawBox(start, colour)
    drawBox(start, colour, PLATE_RADIUS - 50)

for plate in BLUE_PLATES:
    drawBox(plate, BLUE)

for plate in GREEN_PLATES:
    drawBox(plate, GREEN)

for holder in CHERRY_HOLDERS:
    drawCherryBox(holder)

start_state = board.copy()

# To Refresh the board
def refresh(board):
    board = start_state.copy()
    for pucks, colour in puck_list:
        for puck in pucks:
            drawPuck(board, puck, colour)

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


board = refresh(board)
plt.imshow(board)

plt.show()
