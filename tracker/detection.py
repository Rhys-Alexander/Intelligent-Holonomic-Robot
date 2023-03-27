import cv2
import numpy as np
from shapely.geometry import LineString
from shapely import centroid

DICTIONAIRY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
PARAMS = cv2.aruco.DetectorParameters()
DETECTOR = cv2.aruco.ArucoDetector(DICTIONAIRY, PARAMS)
WIDTH, HEIGHT = 2000, 3000
XOFFSET, YOFFSET = 570, 575


class Detector:
    def __init__(self, img, size, height, goal_height):
        self.GOAL_HEIGHT = goal_height
        self.HEIGHT = height
        # self.SIZE = size
        # self.OFFSET = size // 2 - 500
        self.bot = None
        self.goals = None
        self.obstacles = None
        self.matrix = None
        self.CAM_POS = (1000, -300, 1700)
        try:
            self.matrix = self.getMatrix(img)
        except:
            print("no aruco grid found")

    def camera_compensation(self, x, y, height):
        line = LineString((self.CAM_POS[:2], (x, y)))
        distance = line.length - height / (self.CAM_POS[2] / line.length)
        actual_pos = line.interpolate(distance)
        x, y = int(actual_pos.x), int(actual_pos.y)
        return x, y

    def getMatrix(self, frame):
        grid = [0] * 4
        corners, ids, _ = DETECTOR.detectMarkers(frame)
        for (corner, id) in zip(corners, ids):
            if not id in range(20, 24):
                continue
            tl, _, br, _ = corner.reshape((4, 2))
            cX = int((tl[0] + br[0]) / 2.0)
            cY = int((tl[1] + br[1]) / 2.0)
            grid[id[0] % 20] = (cX, cY)
        pts1 = np.float32(grid)
        pts2 = np.float32(
            [
                [XOFFSET, YOFFSET],
                [WIDTH - XOFFSET, YOFFSET],
                [XOFFSET, HEIGHT - YOFFSET],
                [WIDTH - XOFFSET, HEIGHT - YOFFSET],
            ]
        )
        return cv2.getPerspectiveTransform(pts1, pts2)

    # TODO have detect markers run once and then use the corners and ids to find the bots and goals
    # TODO speed
    def setBots(self):
        bot = None
        obstacles = []
        corners, ids, _ = DETECTOR.detectMarkers(self.frame)
        for (corner, id) in zip(corners, ids):
            if not id in range(1, 11):
                continue
            tl, _, br, bl = corner.reshape((4, 2))
            cX, cY = int((tl[0] + br[0]) / 2.0), int((tl[1] + br[1]) / 2.0)
            if id == 1:
                rot = np.arctan2(br[1] - bl[1], br[0] - bl[0])
                bot = (cX, cY, rot)
            else:
                obstacles.append((cX, cY, rot))
        if bot:
            rot = bot[2]
            bot = cv2.perspectiveTransform(np.float32([[bot[:2]]]), self.matrix)[0]
            x, y = self.camera_compensation(int(bot[0][0]), int(bot[0][1]), self.HEIGHT)
            self.bot = (x, y, rot)
        if obstacles:
            obstacles = cv2.perspectiveTransform(np.float32([obstacles]), self.matrix)[
                0
            ]
            self.obstacles = []
            for obstacle in obstacles:
                x, y = self.camera_compensation(
                    int(obstacle[0]), int(obstacle[1]), self.HEIGHT
                )
                self.obstacles.append((x, y))

    # TODO integrate with setBots
    def setGoals(self):
        goals = []
        corners, ids, _ = DETECTOR.detectMarkers(self.warped_frame)
        for corner, id in zip(corners, ids):
            if not id in [47, 13, 36]:
                continue
            tl, _, br, bl = corner.reshape((4, 2))
            cX, cY = int((tl[0] + br[0]) / 2.0), int((tl[1] + br[1]) / 2.0)
            c = centroid(LineString([br, bl]))
            x, y = int(cX + 2 * (cX - c.x)), int(cY + 2 * (cY - c.y))
            goals.append(self.camera_compensation(x, y, self.GOAL_HEIGHT * 2))
        self.goals = goals

    def getItems(self, frame):
        self.frame = frame
        self.warped_frame = cv2.warpPerspective(frame, self.matrix, (WIDTH, HEIGHT))
        self.setBots()
        self.setGoals()
        return self.bot, self.goals, self.obstacles, self.warped_frame
