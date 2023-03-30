import math

import numpy as np
from shapely.geometry import Point, LineString

ENEMY_WEIGHT = 10**8.5


class PathFinder:
    def __init__(self, bot_radius):
        self.bot_radius = bot_radius

    def update(self, pucks, bot, enemies):
        if bot is None:
            print("Bot not found")
            return "0,0,0\n", None, None, None
        self.set_items(pucks, bot, enemies)
        self.make_graph()
        self.path = self.get_puck()
        return self.get_x_y_rot_vel(self.path), self.path, self.graph, self.items

    def get_x_y_rot_vel(self, point):
        vel = 100
        saturated_dist = 400
        if point is None:
            return "0,0,0\n"
        x, y, rot = self.bot
        x2, y2 = point
        dx, dy = x2 - x, y2 - y
        d = math.dist((x, y), point)
        if d < (self.bot_radius):
            print("Puck found")
            return "0,0,0\n"
        if d < saturated_dist:
            vel = (d // saturated_dist) * vel
            vel = vel if abs(vel) > 40 else 40
        theta = math.atan2(dy, dx) - rot
        x_vel = int(vel * math.sin(theta))
        y_vel = int(vel * math.cos(theta))
        rot_vel = int(75 * theta / math.pi)
        return ",".join(str(x) for x in [x_vel, y_vel, rot_vel]) + "\n"

    def set_items(self, pucks, bot, enemies):
        self.pucks = pucks
        self.bot = bot
        self.enemies = enemies
        self.items = self.pucks + [self.bot[:2]]

    def check_collisions(self, line_ends):
        margin = self.bot_radius * 2
        line = LineString(line_ends)
        if self.enemies:
            for bot in self.enemies:
                obstacle = Point(*bot)
                if line.distance(obstacle) <= margin:
                    return True

    def make_graph(self):
        graph = np.zeros((len(self.items) - 1))
        for i, item in enumerate(self.items[:-1]):
            # Put in graph if no collisions with weight of distance plus inverse square of distance to enemy bot
            if not self.check_collisions([item, self.bot[:2]]):
                weight = math.dist(item, self.bot[:2])
                if self.enemies:
                    for bot in self.enemies:
                        weight += ENEMY_WEIGHT / (
                            (LineString([item, self.bot[:2]]).distance(Point(bot))) ** 2
                            + 1
                        )
                graph[i] = weight
        self.graph = graph

    def get_puck(self):
        pairs = {j: node for j, node in enumerate(self.graph) if node != 0}
        try:
            next = min(pairs, key=pairs.get)
            return self.items[next]
        except ValueError:
            print("No puck found")
            return None
