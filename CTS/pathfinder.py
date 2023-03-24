import math
import visualiser as vis

import numpy as np
from shapely.geometry import Point, LineString, Polygon

# Integer Radiuses
PUCK_RADIUS = 60
PLATE_RADIUS = 225
BOT_RADIUS = 200
CHERRY_BOT_RADIUS = 160
CHERRY_RADIUS = 15

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
CHERRY_COLLECT = [
    (965 - CHERRY_BOT_RADIUS, CHERRY_BOT_RADIUS),
    (35 + CHERRY_BOT_RADIUS, 1500),
    (1965 - CHERRY_BOT_RADIUS, 1500),
    (1035 + CHERRY_BOT_RADIUS, 3000 - CHERRY_BOT_RADIUS),
]
CHERRY_WAYPOINTS = [
    (965 - CHERRY_BOT_RADIUS, 300 + CHERRY_BOT_RADIUS),
    (35 + CHERRY_BOT_RADIUS, 1500),
    (1965 - CHERRY_BOT_RADIUS, 1500),
    (1035 + CHERRY_BOT_RADIUS, 2700 - CHERRY_BOT_RADIUS),
]

ENEMY_BOT_WEIGHT = 10**8.5


class PathFinder:
    def __init__(self, blueTeam):
        self.platter = BLUE_START_CENTRE if blueTeam else GREEN_START_CENTRE
        self.enemy_platter = GREEN_START if blueTeam else BLUE_START
        self.PLATE_CENTRES = BLUE_PLATE_CENTRES if blueTeam else GREEN_PLATE_CENTRES
        self.plates = BLUE_PLATES if blueTeam else GREEN_PLATES
        self.blueTeam = blueTeam

    def update(self, pucks, bot, cherryBot, enemyBots, cherries, capacity):
        self.capacity = capacity
        self.setItems(pucks, bot, cherryBot, enemyBots, cherries)
        self.makeBotGraph()
        self.makeCherryGraph()
        self.bot_path = self.getBotPath()
        self.cherry_path = self.getCherryPath()
        botCmd = self.getXYRotVel(self.bot, self.bot_path)
        # cherryCmd = self.getXYRotVel(self.cherry_bot, self.cherry_path)
        return botCmd

    def getXYRotVel(self, bot, point):
        MAX_VEL = 100
        if point is None:
            return "0,0,0\n"
        x, y, rot = bot
        x2, y2 = point
        dx, dy = x2 - x, y2 - y
        theta = math.atan2(dy, dx) - rot
        xVel = MAX_VEL * math.sin(theta)
        yVel = MAX_VEL * math.cos(theta)
        rotVel = MAX_VEL * theta / math.pi
        return ",".join(str(x) for x in [xVel, yVel, rotVel]) + "\n"

    def setItems(self, pucks, bot, cherryBot, enemyBots, cherries):
        self.pucks = pucks
        self.bot = bot
        self.cherry_bot = cherryBot
        self.enemy_bots = enemyBots
        self.cherries = cherries
        self.waypoints = CHERRY_WAYPOINTS

        captive_pucks = []
        for puck in self.pucks:
            for plate in self.plates + [self.enemy_platter]:
                p1x, p1y = plate[0]
                p2x, p2y = plate[1]
                if (
                    p1x - PUCK_RADIUS <= puck[0] <= p2x + PUCK_RADIUS
                    and p1y - PUCK_RADIUS <= puck[1] <= p2y + PUCK_RADIUS
                ):
                    captive_pucks.append(puck)
        free_pucks = [puck for puck in self.pucks if puck not in captive_pucks]
        self.free_pucks = free_pucks
        self.captive_pucks = captive_pucks

        self.cherry_items = self.waypoints + [self.cherry_bot[:2]]
        self.items = self.free_pucks + self.PLATE_CENTRES + [self.bot[:2]]

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
        for holder in CHERRY_HOLDERS:
            x1, y1 = holder[0]
            x2, y2 = holder[1]
            if (
                Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)]).distance(
                    LineString(line_ends)
                )
                <= bot_radius
            ):
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
                    + max(
                        ENEMY_BOT_WEIGHT
                        * 1
                        / (
                            (LineString([item, self.bot[:2]]).distance(Point(bot))) ** 2
                            + 1
                        )
                        for bot in self.enemy_bots
                    )
                )
        self.bot_graph = graph

    def makeCherryGraph(self):
        graph = np.zeros((len(self.cherry_items) - 1))
        for i, item in enumerate(self.cherry_items[:-1]):
            # Put in graph if no collisions with weight of distance plus inverse square of distance to enemy bot
            if not self.checkCollisions(
                [item, self.cherry_bot[:2]],
                CHERRY_BOT_RADIUS,
                self.enemy_bots + [self.bot],
            ):
                graph[i] = (
                    math.dist(item, self.cherry_bot[:2])
                    + 1
                    + max(
                        ENEMY_BOT_WEIGHT
                        * 1
                        / (
                            (
                                LineString([item, self.cherry_bot[:2]]).distance(
                                    Point(bot)
                                )
                            )
                            ** 2
                            + 1
                        )
                        for bot in self.enemy_bots + [self.bot]
                    )
                )
        self.cherry_graph = graph

    def displayGraph(self, img=False):
        board = vis.Board(img)
        board.drawItems(
            self.bot,
            self.cherry_bot,
            self.enemy_bots,
            pucks=self.pucks,
            cherries=self.cherries,
        )
        board.drawGraph(self.bot_graph, self.items, self.bot)
        board.drawGraph(self.cherry_graph, self.cherry_items, self.cherry_bot)
        board.drawPath(self.bot_path, self.bot)
        board.drawPath(self.cherry_path, self.cherry_bot)
        board.display()

    def getPuck(self):
        edges = self.bot_graph[: -len(self.PLATE_CENTRES)]
        pairs = {j: node for j, node in enumerate(edges) if node != 0}
        try:
            next = min(pairs, key=pairs.get)
            return self.items[next]
        except ValueError:
            print("No puck found")
            return None

    def getPlate(self):
        edges = self.bot_graph[-len(self.PLATE_CENTRES) :]
        pairs = {j: node for j, node in enumerate(edges) if node != 0}
        try:
            next = min(pairs, key=pairs.get)
            return self.items[next + len(self.items) - len(self.PLATE_CENTRES)]
        except ValueError:
            print("No plate found")
            return None

    def getBotPath(self):
        return (
            self.getPuck()
            if self.capacity > 0 and len(self.free_pucks) > 0
            else self.getPlate()
        )

    def getCherryPath(self):
        edges = self.cherry_graph[:-1]
        pairs = {j: node for j, node in enumerate(edges) if node != 0}
        try:
            next = min(pairs, key=pairs.get)
            return self.cherry_items[next]
        except ValueError:
            print("No cherry path found")


# FIXME not efficient and simple enough for the secondary robot
# TODO make cherry paths simpler
