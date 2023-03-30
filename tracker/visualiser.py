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
        self.goal_radius = goal_radius
        self.bot_radius = bot_radius

    def draw_goal(self, pt):
        x, y = pt
        cv2.circle(
            self.view,
            center=(x, y),
            radius=self.goal_radius,
            color=YELLOW,
            thickness=ITEM_THICKNESS,
        )

    def draw_bot(self, bot, colour, radius):
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

    def draw_graph(self, graph, nodes, bot):
        for i, x in enumerate(graph):
            if x:
                cv2.line(
                    self.view,
                    pt1=nodes[i],
                    pt2=bot[:2],
                    color=BLUE,
                    thickness=GRAPH_THICKNESS,
                )

    def draw_path(self, path, bot):
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
                self.draw_goal(goal)
        if enemies:
            for enemy in enemies:
                self.draw_bot(enemy, RED, self.bot_radius)
        if bot:
            self.draw_bot(bot, BLUE, self.bot_radius)
            self.draw_graph(graph, nodes, bot)
            if path:
                self.draw_path(path, bot)
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
