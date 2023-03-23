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

# TODO ignore pucks if inside robot, check if prob  first
# TODO figure out which bot is which


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
        for (markerCorner, markerID) in zip(corners, ids):
            if not markerID in range(20, 24):
                continue
            tl, _, br, _ = markerCorner.reshape((4, 2))
            cX = int((tl[0] + br[0]) / 2.0)
            cY = int((tl[1] + br[1]) / 2.0)
            grid[markerID[0] % 20] = (cX, cY)
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

    # TODO get which bot is which
    def setBots(self):
        bots = []
        rots = []
        corners, ids, _ = DETECTOR.detectMarkers(self.frame)
        for (markerCorner, markerID) in zip(corners, ids):
            if not markerID in range(1, 11):
                continue
            tl, _, br, bl = markerCorner.reshape((4, 2))
            cX, cY = int((tl[0] + br[0]) / 2.0), int((tl[1] + br[1]) / 2.0)
            rots.append(np.arctan2(bl[1] - br[1], bl[0] - br[0]))
            bots.append((cX, cY))
        if bots:
            og_bots = cv2.perspectiveTransform(np.float32([bots]), self.matrix)[0]
            self.bots = []
            for bot, rot in zip(og_bots, rots):
                x, y = self.camera_compensation(int(bot[0]), int(bot[1]), BOT_HEIGHT)
                self.bots.append((x, y, rot))

    def setPucks(self):
        pucks = []
        corners, ids, _ = DETECTOR.detectMarkers(self.warped_frame)
        for markerCorner, id in zip(corners, ids):
            if not id in [47, 13, 36]:
                continue
            tl, _, br, bl = markerCorner.reshape((4, 2))
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
        return self.bots, self.pucks, self.warped_frame
