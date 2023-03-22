import math
import cv2
import numpy as np

# import matplotlib.pyplot as plt

# y,x
BOARD_DIMENSIONS = (3000, 2000)

# Colours, BGR
RED = (0, 0, 255)
GREEN = (18, 170, 0)
BLUE = (230, 92, 0)
PINK = (195, 0, 195)
YELLOW = (0, 191, 255)
BROWN = (23, 15, 46)
GRAY = (153, 184, 173)

# Thicknesses
BOARD_THICKNESS = 10
ITEM_THICKNESS = 15
BOT_THICKNESS = 20
GRAPH_THICKNESS = 2
PATH_THICKNESS = 10

# Integer Radiuses
PUCK_RADIUS = 60
BOT_RADIUS = 200
CHERRY_BOT_RADIUS = 160

# 2 length tuple, x pos and y pos
BLUE_START = ((0, 0), (450, 450))
GREEN_START = ((1550, 0), (2000, 450))
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


class Board:
    def __init__(self, img=False):
        self.board = (
            255 * np.ones(shape=[*BOARD_DIMENSIONS, 3], dtype=np.uint8)
            if img is False
            else img
        )

        for start, colour in ((BLUE_START, BLUE), (GREEN_START, GREEN)):
            self.drawBox(start, colour)
            self.drawBox(start, colour, radius_modifier=-50)

        for plate in BLUE_PLATES:
            self.drawBox(plate, BLUE)

        for plate in GREEN_PLATES:
            self.drawBox(plate, GREEN)

        for holder in CHERRY_HOLDERS:
            self.drawBox(holder, GRAY)

        self.blank_state = self.board.copy()

    def drawBox(self, pt, colour, radius_modifier=0):
        p1, p2 = pt
        if radius_modifier:
            p1 = (p1[0] - radius_modifier, p1[1] - radius_modifier)
            p2 = (p2[0] + radius_modifier, p2[1] + radius_modifier)
        cv2.rectangle(
            self.board,
            pt1=p1,
            pt2=p2,
            color=colour,
            thickness=BOARD_THICKNESS,
        )

    def drawPuck(self, pt):
        x, y = pt
        cv2.circle(
            self.board,
            center=(x, y),
            radius=PUCK_RADIUS,
            color=RED,
            thickness=ITEM_THICKNESS,
        )

    def drawCherry(self, pt):
        x, y = pt
        cv2.line(
            self.board,
            pt1=(x, y - 80),
            pt2=(x, y + 80),
            color=RED,
            thickness=ITEM_THICKNESS,
        )

    def drawBot(self, bot, colour, radius):
        x, y, rot = bot
        cv2.circle(
            self.board,
            center=(x, y),
            radius=radius,
            color=colour,
            thickness=BOT_THICKNESS,
        )
        cv2.line(
            self.board,
            pt1=(x, y),
            pt2=(
                math.ceil(x + radius * np.cos(rot)),
                math.ceil(y + radius * np.sin(rot)),
            ),
            color=colour,
            thickness=BOT_THICKNESS,
        )

    def drawItems(
        self,
        bot,
        cherry_bot,
        enemy_bots,
        pucks=False,
        cherries=False,
    ):
        self.board = self.blank_state.copy()
        for puck in pucks:
            self.drawPuck(puck)

        if cherries:
            for cherry in cherries:
                self.drawCherry(cherry)

        self.drawBot(cherry_bot, RED, CHERRY_BOT_RADIUS)
        self.drawBot(bot, RED, BOT_RADIUS)
        for bot in enemy_bots:
            self.drawBot(bot, GRAY, BOT_RADIUS)

    def drawGraph(self, graph, nodes, bot):
        for i, x in enumerate(graph):
            if x:
                cv2.line(
                    self.board,
                    pt1=nodes[i],
                    pt2=bot[:2],
                    color=RED,
                    thickness=GRAPH_THICKNESS,
                )

    def drawPath(self, path, bot):
        cv2.line(
            self.board,
            pt1=path,
            pt2=bot[:2],
            color=GREEN,
            thickness=PATH_THICKNESS,
        )

    def display(self):
        cv2.imshow("Board", self.board)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
