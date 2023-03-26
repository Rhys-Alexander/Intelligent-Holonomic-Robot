import math
import visualiser as vis

import numpy as np
from shapely.geometry import Point, LineString, Polygon

# Integer Radiuses
PUCK_RADIUS = 60
BOT_RADIUS = 155
ENEMY_BOT_WEIGHT = 10**8.5


class PathFinder:
    def __init__(self):
        pass

    def update(self, pucks, bot, enemyBots, capacity):
        self.capacity = capacity
        self.setItems(pucks, bot, enemyBots)
        self.makeBotGraph()
        self.bot_path = self.getBotPath()
        botCmd = self.getXYRotVel(self.bot, self.bot_path)
        return botCmd

    def getXYRotVel(self, bot, point):
        MAX_VEL = 100
        if point is None:
            return "0,0,0\n"
        x, y, rot = bot
        x2, y2 = point
        dx, dy = x2 - x, y2 - y

        # if math.dist(bot, point) < (BOT_RADIUS + 50):
        #     return "0,0,0\n"
        theta = math.atan2(dy, dx) - rot
        xVel = MAX_VEL * math.sin(theta)
        yVel = MAX_VEL * math.cos(theta)
        rotVel = 50 * theta / math.pi
        return ",".join(str(x) for x in [xVel, yVel, rotVel]) + "\n"

    def setItems(self, pucks, bot, enemyBots):
        self.pucks = pucks
        self.bot = bot
        self.enemy_bots = enemyBots
        self.items = self.pucks + [self.bot[:2]]

    def checkCollision(self, line_ends, obstacle, bot_radius, radius):
        margin = bot_radius + radius
        obstacle = Point(*obstacle)
        line = LineString(line_ends)
        if line.distance(obstacle) <= margin:
            return True

    def checkCollisions(self, line_ends, bot_radius, other_bots):
        for bot in other_bots:
            if self.checkCollision(line_ends, bot, bot_radius, BOT_RADIUS):
                return True

    def makeBotGraph(self):
        graph = np.zeros((len(self.items) - 1))
        for i, item in enumerate(self.items[:-1]):
            # Put in graph if no collisions with weight of distance plus inverse square of distance to enemy bot
            if not self.checkCollisions(
                [item, self.bot[:2]], BOT_RADIUS, self.enemy_bots
            ):
                graph[i] = (
                    math.dist(item, self.bot[:2])
                    + 1
                    # FIXME fix this
                    # + max(
                    #     ENEMY_BOT_WEIGHT
                    #     * 1
                    #     / (
                    #         (LineString([item, self.bot[:2]]).distance(Point(bot))) ** 2
                    #         + 1
                    #     )
                    #     for bot in self.enemy_bots
                    # )
                )
        self.bot_graph = graph

    def displayGraph(self, img=False):
        board = vis.Board(img)
        board.drawItems(
            self.bot,
            self.enemy_bots,
            pucks=self.pucks,
        )
        board.drawGraph(self.bot_graph, self.items, self.bot)
        board.drawPath(self.bot_path, self.bot)
        board.display()

    def getPuck(self):
        edges = self.bot_graph
        pairs = {j: node for j, node in enumerate(edges) if node != 0}
        try:
            next = min(pairs, key=pairs.get)
            return self.items[next]
        except ValueError:
            print("No puck found")
            return None

    def getBotPath(self):
        return self.getPuck()


# FIXME not efficient and simple enough for the secondary robot
# TODO make cherry paths simpler
