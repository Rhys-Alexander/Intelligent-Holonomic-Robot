import cv2
import numpy as np
from shapely.geometry import LineString
import shapely

DICTIONAIRY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
WIDTH, HEIGHT = 2000, 3000
CODE_X_OFFSET, CODE_Y_OFFSET = 570, 575
PARAMS = cv2.aruco.DetectorParameters()
DETECTOR = cv2.aruco.ArucoDetector(DICTIONAIRY, PARAMS)
BOT_HEIGHT = 430
PUCK_HEIGHT = 20


class Detector:
    def __init__(self, blueTeam, img):
        self.blueTeam = blueTeam
        self.CAM_POS = (900, -200, 1500) if blueTeam else (1100, -200, 1500)
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
        if len(corners) > 0:
            ids = ids.flatten()
            for (markerCorner, markerID) in zip(corners, ids):
                tl, _, br, _ = markerCorner.reshape((4, 2))
                cX = int((tl[0] + br[0]) / 2.0)
                cY = int((tl[1] + br[1]) / 2.0)
                if markerID in range(20, 24):
                    grid[markerID % 20] = (cX, cY)
        pts1 = np.float32(grid)
        pts2 = np.float32(
            [
                [CODE_X_OFFSET, CODE_Y_OFFSET],
                [WIDTH - CODE_X_OFFSET, CODE_Y_OFFSET],
                [CODE_X_OFFSET, HEIGHT - CODE_Y_OFFSET],
                [WIDTH - CODE_X_OFFSET, HEIGHT - CODE_Y_OFFSET],
            ]
        )
        return cv2.getPerspectiveTransform(pts1, pts2)

    def setBots(self, frame):
        bots = []
        corners, ids, _ = DETECTOR.detectMarkers(frame)
        if len(corners) > 0:
            ids = ids.flatten()
            for (markerCorner, markerID) in zip(corners, ids):
                tl, _, br, _ = markerCorner.reshape((4, 2))
                cX = int((tl[0] + br[0]) / 2.0)
                cY = int((tl[1] + br[1]) / 2.0)
                if markerID in range(1, 11):
                    bots.append((cX, cY))
        if bots:
            og_bots = cv2.perspectiveTransform(np.float32([bots]), self.matrix)[0]
            self.bots = [
                self.camera_compensation(int(bot[0]), int(bot[1]), BOT_HEIGHT)
                for bot in og_bots
            ]

    def setPucks(self, frame):
        corners, ids, _ = DETECTOR.detectMarkers(frame)
        if not len(corners) > 0:
            return frame
        pucks = []
        for markerCorner, id in zip(corners, ids):
            tl, _, br, bl = markerCorner.reshape((4, 2))
            x = int((tl[0] + br[0]) / 2.0)
            y = int((tl[1] + br[1]) / 2.0)
            if id in [47, 13, 36]:
                c = shapely.centroid(LineString([br, bl]))
                x2, y2 = int(c.x), int(c.y)
                x, y = x + 2 * (x - x2), y + 2 * (y - y2)
                cv2.circle(frame, (x, y), 5, (0, 0, 255), 20)
                x, y = self.camera_compensation(x, y, PUCK_HEIGHT * 2)
                cv2.circle(frame, (x, y), 5, (0, 255, 0), 10)
                pucks.append((x, y))
        self.pucks = pucks

    def getItems(self, frame):
        self.setBots(frame)
        frame = cv2.warpPerspective(frame, self.matrix, (WIDTH, HEIGHT))
        self.setPucks(frame)
        for bot in self.bots:
            cv2.circle(frame, bot, 5, (0, 0, 255), 20)
        cv2.imwrite("CTS/output_pics/warped.jpeg", frame)
        return self.bots, self.pucks
