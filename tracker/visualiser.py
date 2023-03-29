import math

import cv2
import numpy as np

# Colours, BGR
RED = (0, 0, 255)
GREEN = (18, 170, 0)
BLUE = (230, 92, 0)
YELLOW = (0, 191, 255)

# Thicknesses
ITEM_THICKNESS = 15
BOT_THICKNESS = 20
GRAPH_THICKNESS = 2
PATH_THICKNESS = 10


class View:
    def __init__(self, goal_radius, bot_radius) -> None:
        self.GOAL_RADIUS = goal_radius
        self.BOT_RADIUS = bot_radius

    def drawGoal(self, pt):
        x, y = pt
        cv2.circle(
            self.view,
            center=(x, y),
            radius=self.GOAL_RADIUS,
            color=YELLOW,
            thickness=ITEM_THICKNESS,
        )

    def drawBot(self, bot, colour, radius):
        if len(bot) == 3:
            x, y, rot = bot
        else:
            x, y = bot
            rot = None
        cv2.circle(
            self.view,
            center=(x, y),
            radius=radius,
            color=colour,
            thickness=BOT_THICKNESS,
        )
        if rot:
            cv2.line(
                self.view,
                pt1=(x, y),
                pt2=(
                    math.ceil(x + radius * np.cos(rot)),
                    math.ceil(y + radius * np.sin(rot)),
                ),
                color=colour,
                thickness=BOT_THICKNESS,
            )
            cv2.putText(
                self.view,
                str(round(math.degrees(rot), 2)),
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                2,
                RED,
                8,
            )

    def drawGraph(self, graph, nodes, bot):
        for i, x in enumerate(graph):
            if x:
                cv2.line(
                    self.view,
                    pt1=nodes[i],
                    pt2=bot[:2],
                    color=BLUE,
                    thickness=GRAPH_THICKNESS,
                )

    def drawPath(self, path, bot):
        cv2.line(
            self.view,
            pt1=path,
            pt2=bot[:2],
            color=GREEN,
            thickness=PATH_THICKNESS,
        )

    def update(
        self,
        bot,
        enemies,
        goals,
        path,
        graph,
        nodes,
        img,
        cmd,
    ):
        self.view = img
        if goals:
            for goal in goals:
                self.drawGoal(goal)
        if enemies:
            for enemy in enemies:
                self.drawBot(enemy, RED, self.BOT_RADIUS)
        if bot:
            self.drawBot(bot, BLUE, self.BOT_RADIUS)
            self.drawGraph(graph, nodes, bot)
            if path:
                self.drawPath(path, bot)
        if cmd:
            cv2.putText(
                self.view,
                cmd.strip(),
                (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                3,
                RED,
                10,
            )
        return self.view
