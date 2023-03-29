import math

import numpy as np
from shapely.geometry import Point, LineString

ENEMY_WEIGHT = 10**8.5


class PathFinder:
    def __init__(self, bot_radius):
        self.BOT_RADIUS = bot_radius

    def update(self, pucks, bot, enemies):
        if bot is None:
            print("Bot not found")
            return "0,0,0\n", None, None, None
        self.setItems(pucks, bot, enemies)
        self.makeGraph()
        self.path = self.getPuck()
        return self.getXYRotVel(self.path), self.path, self.graph, self.items

    def getXYRotVel(self, point):
        vel = 100
        saturated_dist = 400
        if point is None:
            return "0,0,0\n"
        x, y, rot = self.bot
        x2, y2 = point
        dx, dy = x2 - x, y2 - y
        d = math.dist((x, y), point)
        if d < (self.BOT_RADIUS):
            print("Puck found")
            return "0,0,0\n"
        if d < saturated_dist:
            vel = (d // saturated_dist) * vel
            vel = vel if abs(vel) > 40 else 40
        theta = math.atan2(dy, dx) - rot
        xVel = int(vel * math.sin(theta))
        yVel = int(vel * math.cos(theta))
        rotVel = int(75 * theta / math.pi)
        return ",".join(str(x) for x in [xVel, yVel, rotVel]) + "\n"

    def setItems(self, pucks, bot, enemies):
        self.pucks = pucks
        self.bot = bot
        self.enemies = enemies
        self.items = self.pucks + [self.bot[:2]]

    def checkCollisions(self, line_ends):
        margin = self.BOT_RADIUS * 2
        line = LineString(line_ends)
        if self.enemies:
            for bot in self.enemies:
                obstacle = Point(*bot)
                if line.distance(obstacle) <= margin:
                    return True

    def makeGraph(self):
        graph = np.zeros((len(self.items) - 1))
        for i, item in enumerate(self.items[:-1]):
            # Put in graph if no collisions with weight of distance plus inverse square of distance to enemy bot
            if not self.checkCollisions([item, self.bot[:2]]):
                weight = math.dist(item, self.bot[:2])
                if self.enemies:
                    for bot in self.enemies:
                        weight += ENEMY_WEIGHT / (
                            (LineString([item, self.bot[:2]]).distance(Point(bot))) ** 2
                            + 1
                        )
                graph[i] = weight
        self.graph = graph

    def getPuck(self):
        pairs = {j: node for j, node in enumerate(self.graph) if node != 0}
        try:
            next = min(pairs, key=pairs.get)
            return self.items[next]
        except ValueError:
            print("No puck found")
            return None
