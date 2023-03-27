import cv2
import numpy as np
from shapely.geometry import LineString
from shapely import centroid

DICTIONAIRY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
PARAMS = cv2.aruco.DetectorParameters()
DETECTOR = cv2.aruco.ArucoDetector(DICTIONAIRY, PARAMS)


class Detector:
    def __init__(self, img, size, height, goal_height):
        self.GOAL_HEIGHT = goal_height
        self.HEIGHT = height
        self.SIZE = size
        self.OFFSET = size // 2 - 500
        self.bot = None
        self.goals = None
        self.obstacles = None
        self.CAM_POS = (1000, -300, 1700)
        while True:
            try:
                self.matrix = self.getMatrix(img)
                break
            except:
                print("no aruco grid found")
                pass

    def camera_compensation(self, x, y, height):
        line = LineString((self.CAM_POS[:2], (x, y)))
        distance = line.length - height / (self.CAM_POS[2] / line.length)
        actual_pos = line.interpolate(distance)
        x, y = int(actual_pos.x), int(actual_pos.y)
        return x, y

    def getMatrix(self, frame):
        grid = [0] * 4
        corners, ids, _ = DETECTOR.detectMarkers(frame)
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        cv2.imwrite("aruco.png", frame)
        for (corner, id) in zip(corners, ids):
            if not id in range(20, 24):
                continue
            tl, _, br, _ = corner.reshape((4, 2))
            cX = int((tl[0] + br[0]) / 2.0)
            cY = int((tl[1] + br[1]) / 2.0)
            grid[id[0] % 20] = (cX, cY)
        grid = [grid[0], grid[3], grid[1], grid[2]]
        pts1 = np.float32(grid)
        pts2 = np.float32(
            [
                [self.OFFSET, self.OFFSET],
                [self.SIZE - self.OFFSET, self.OFFSET],
                [self.OFFSET, self.SIZE - self.OFFSET],
                [self.SIZE - self.OFFSET, self.SIZE - self.OFFSET],
            ]
        )
        return cv2.getPerspectiveTransform(pts1, pts2)

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
        self.warped_frame = cv2.warpPerspective(
            frame, self.matrix, (self.SIZE, self.SIZE)
        )
        self.setBots()
        self.setGoals()
        return self.bot, self.goals, self.obstacles, self.warped_frame