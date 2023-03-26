import cv2
import numpy as np
from shapely.geometry import LineString
import shapely

DICTIONAIRY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
WIDTH, HEIGHT = 2000, 2000
CODE_OFFSET = 500
PARAMS = cv2.aruco.DetectorParameters()
DETECTOR = cv2.aruco.ArucoDetector(DICTIONAIRY, PARAMS)
BOT_HEIGHT = 90
PUCK_HEIGHT = 10


class Detector:
    def __init__(self, img):
        self.CAM_POS = (1000, -300, 1700)
        while True:
            try:
                self.matrix = self.getMatrix(img)
                break
            except cv2.error:
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
                [CODE_OFFSET, CODE_OFFSET],
                [WIDTH - CODE_OFFSET, CODE_OFFSET],
                [CODE_OFFSET, HEIGHT - CODE_OFFSET],
                [WIDTH - CODE_OFFSET, HEIGHT - CODE_OFFSET],
            ]
        )
        return cv2.getPerspectiveTransform(pts1, pts2)

    def setBots(self):
        bots = [] * 10
        rots = [] * 10
        corners, ids, _ = DETECTOR.detectMarkers(self.frame)
        for (corner, id) in zip(corners, ids):
            if not id in range(1, 11):
                continue
            tl, _, br, bl = corner.reshape((4, 2))
            cX, cY = int((tl[0] + br[0]) / 2.0), int((tl[1] + br[1]) / 2.0)
            rots[id - 1](np.arctan2(bl[1] - br[1], bl[0] - br[0]))
            bots[id - 1]((cX, cY))
        if bots:
            bots = cv2.perspectiveTransform(np.float32([bots]), self.matrix)[0]
            self.enemies = []
            for i, (bot, rot) in enumerate(zip(bots, rots)):
                x, y = self.camera_compensation(int(bot[0]), int(bot[1]), BOT_HEIGHT)
                if i == 1:
                    self.bot = (x, y, rot)
                else:
                    self.enemies.append((x, y, rot))

    def setPucks(self):
        pucks = []
        corners, ids, _ = DETECTOR.detectMarkers(self.warped_frame)
        for corner, id in zip(corners, ids):
            if not id in [47, 13, 36]:
                continue
            tl, _, br, bl = corner.reshape((4, 2))
            cX, cY = int((tl[0] + br[0]) / 2.0), int((tl[1] + br[1]) / 2.0)
            c = shapely.centroid(LineString([br, bl]))
            x, y = int(cX + 2 * (cX - c.x)), int(cY + 2 * (cY - c.y))
            pucks.append(self.camera_compensation(x, y, PUCK_HEIGHT * 2))
        self.pucks = pucks

    def getItems(self, frame):
        self.frame = frame
        self.warped_frame = cv2.warpPerspective(frame, self.matrix, (WIDTH, HEIGHT))
        self.setBots()
        self.setPucks()
        return self.bot, self.pucks, self.enemies, self.warped_frame
