import math
import cv2
import numpy as np

# import matplotlib.pyplot as plt

# y,x
BOARD_DIMENSIONS = (2000, 2000)

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


class Board:
    def __init__(
        self,
        img=False,
    ):
        self.board = (
            255 * np.ones(shape=[*BOARD_DIMENSIONS, 3], dtype=np.uint8)
            if img is False
            else img
        )
        self.blank_state = self.board.copy()

    def drawPuck(self, pt):
        x, y = pt
        cv2.circle(
            self.board,
            center=(x, y),
            radius=PUCK_RADIUS,
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
        enemy_bots,
        pucks=False,
    ):
        self.board = self.blank_state.copy()
        for puck in pucks:
            self.drawPuck(puck)
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
