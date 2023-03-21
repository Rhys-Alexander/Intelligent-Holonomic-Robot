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
blueTeam = True
CAM_POS = (900, -200, 1500) if blueTeam else (1100, -200, 1500)


def camera_compensation(x, y, frame, height):
    line = LineString((CAM_POS[:2], (x, y)))
    cv2.line(frame, (int(CAM_POS[0]), int(CAM_POS[1])), (x, y), (0, 0, 255), 2)
    distance = line.length - height / (CAM_POS[2] / line.length)
    actual_pos = line.interpolate(distance)
    x, y = int(actual_pos.x), int(actual_pos.y)
    return x, y


def getMatrixAndBots(frame):
    bots = []
    grid = [0] * 4
    corners, ids, _ = DETECTOR.detectMarkers(frame)
    if len(corners) > 0:
        ids = ids.flatten()
        for (markerCorner, markerID) in zip(corners, ids):
            tl, _, br, _ = markerCorner.reshape((4, 2))
            cX = int((tl[0] + br[0]) / 2.0)
            cY = int((tl[1] + br[1]) / 2.0)
            if markerID in range(1, 11):
                bots.append((cX, cY))
            elif markerID in range(20, 24):
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
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    if bots:
        bots = cv2.perspectiveTransform(np.float32([bots]), matrix)[0]
    return matrix, bots


def getItems(frame, uncomp_bots):
    bots = []
    for bot in uncomp_bots:
        x, y = camera_compensation(int(bot[0]), int(bot[1]), frame, BOT_HEIGHT)
        cv2.circle(frame, (x, y), 5, (0, 0, 255), 20)
        bots.append((x, y))
    corners, ids, _ = DETECTOR.detectMarkers(frame)
    if not len(corners) > 0:
        return frame
    pink = []
    yellow = []
    brown = []
    for markerCorner, id in zip(corners, ids):
        tl, _, br, bl = markerCorner.reshape((4, 2))
        x = int((tl[0] + br[0]) / 2.0)
        y = int((tl[1] + br[1]) / 2.0)
        if id in [47, 13, 36]:
            c = shapely.centroid(LineString([br, bl]))
            x2, y2 = int(c.x), int(c.y)
            x, y = x + 2 * (x - x2), y + 2 * (y - y2)
            cv2.circle(frame, (x, y), 5, (0, 0, 255), 20)
            x, y = camera_compensation(x, y, frame, PUCK_HEIGHT * 2)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), 10)
            if id == 47:
                pink.append((x, y))
            elif id == 13:
                yellow.append((x, y))
            else:
                brown.append((x, y))
    return (pink, yellow, brown, bots)


img = cv2.imread("CTS/pics/multi_bots.jpeg")
while True:
    try:
        matrix, bots = getMatrixAndBots(img)
        break
    except cv2.error:
        print("no aruco")
        pass
img = cv2.warpPerspective(img, matrix, (WIDTH, HEIGHT))
getItems(img, bots)
cv2.imwrite("CTS/pics/warped.jpeg", img)
