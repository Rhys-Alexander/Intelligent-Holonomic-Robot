import cv2
import numpy as np
import matplotlib.pyplot as plt


# Colours
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Integer Diameter
PUCK_DIAMETER = 120
PLATE_RADIUS = 225
# 2 length tuple, x pos and y pos
BLUE_START = (225, 225)
GREEN_START = (1775, 225)
BLUE_PLATES = [(1775, 1125), (225, 1875), (725, 2775), (1775, 2775)]
GREEN_PLATES = [(225, 1125), (1775, 1875), (225, 2775), (1275, 2775)]
# list of top left corners, 30 wide, 300 long
CHERRY_HOLDERS = [(985, 0), (985, 2700), (0, 1350), (1950, 1350)]

# 3 length tuple, x pos, y pos, and rotation
blue_bot = (225, 225, 270)
green_bot = (1775, 225, 270)

# lists of tuples, x pos, y pos
pink = [(225, 575), (1775, 575), (225, 2425), (1775, 2425)]
yellow = [(225, 775), (1775, 775), (225, 2225), (1775, 2225)]
brown = [(725, 1125), (1275, 1125), (725, 1875), (1275, 1875)]
pucks = ((pink, (255, 192, 203)), (yellow, (0, 255, 255)), (brown, (165, 42, 42)))
cherries = []

# Blank board
board = 255 * np.ones(shape=[3000, 2000, 3], dtype=np.uint8)


def drawBox(pt, color):
    x, y = pt
    cv2.rectangle(
        board,
        pt1=(x - PLATE_RADIUS, y - PLATE_RADIUS),
        pt2=(x + PLATE_RADIUS, y + PLATE_RADIUS),
        color=color,
        thickness=10,
    )


def drawPuck(pt, color):
    x, y = pt
    cv2.circle(
        board,
        center=(x, y),
        radius=PUCK_DIAMETER // 2,
        color=color,
        thickness=10,
    )


for plate in BLUE_PLATES:
    drawBox(plate, (0, 0, 255))

for pucks, colour in pucks:
    for puck in pucks:
        drawPuck(puck, colour)

plt.imshow(board)

plt.show()
