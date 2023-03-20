import cv2
import numpy as np
from shapely.geometry import LineString
import shapely

DICTIONAIRY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
BWIDTH, BHEIGHT = 2000, 3000
BW_SEG, BH_SEG = BWIDTH / 7, BHEIGHT / 5
# WIDTH, HEIGHT = int(BWIDTH * 1.2), int(BHEIGHT * 1.2)
WIDTH, HEIGHT = BWIDTH, BHEIGHT
# W_SEG, H_SEG = WIDTH / 12, HEIGHT / 12
W_SEG, H_SEG = 0, 0
PARAMS = cv2.aruco.DetectorParameters()
DETECTOR = cv2.aruco.ArucoDetector(DICTIONAIRY, PARAMS)
BOT_HEIGHT = 430

MAX_CHERRY_CONTOUR = 500
MIN_PUCK_CONTOUR = 1500

PUCK_SORT = lambda y: sorted(
    filter(lambda x: cv2.contourArea(x) > MIN_PUCK_CONTOUR, y),
    key=cv2.contourArea,
    reverse=True,
)[:12]
CHERRY_SORT = lambda y: filter(lambda x: cv2.contourArea(x) < MAX_CHERRY_CONTOUR, y)

HSVCOLORS = (
    (
        (15, 53, 24),
        (0, 100, 255),
        45,
        (20, 20),
        PUCK_SORT,
    ),  # brown
    (
        (333, 60, 60),
        (230, 0, 255),
        45,
        (20, 20),
        PUCK_SORT,
    ),  # pink
    (
        (40, 80, 80),
        (0, 255, 255),
        45,
        (20, 20),
        PUCK_SORT,
    ),  # yellow
    (
        (6, 76, 71),
        (0, 0, 255),
        25,
        (3, 3),
        CHERRY_SORT,
    ),  # red
)

# todo understand this
def camera_compensation(x_coordinate, y_coordinate):
    camera_position = [1100, 500, 1500]  # x,y,z coordinate from origin in mm
    # add 300 to move orgin to under the camera
    offset = 100000
    x_coordinate = (offset - x_coordinate) + (camera_position[0] - offset)

    # perform compensation
    x_compensated = x_coordinate - (BOT_HEIGHT / (camera_position[2] / x_coordinate))
    # if y_coordinate < camera_position[1]:
    y_compensated = y_coordinate - (BOT_HEIGHT / (camera_position[2] / y_coordinate))
    # else:
    #     y_compensated = y_coordinate + (
    #         BOT_HEIGHT / (camera_position[2] / y_coordinate)
    #     )
    # substract the offset
    x_compensated = offset - (x_compensated - (camera_position[0] - offset))
    print(x_compensated, y_compensated)

    return int(x_compensated), int(y_compensated)


def getWarpMatrix(frame):
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
            [W_SEG + BW_SEG * 2, H_SEG + BH_SEG],
            [W_SEG + BWIDTH - BW_SEG * 2, H_SEG + BH_SEG],
            [W_SEG + BW_SEG * 2, H_SEG + BH_SEG * 4],
            [W_SEG + BWIDTH - BW_SEG * 2, H_SEG + BH_SEG * 4],
        ]
    )
    return cv2.getPerspectiveTransform(pts1, pts2)


def getPucks(frame):
    corners, ids, _ = DETECTOR.detectMarkers(frame)
    if not len(corners) > 0:
        return frame
    pink = []
    yellow = []
    brown = []
    for markerCorner, id in zip(corners, ids):
        if not id in [47, 13, 36]:
            continue
        tl, _, br, bl = markerCorner.reshape((4, 2))
        x = int((tl[0] + br[0]) / 2.0)
        y = int((tl[1] + br[1]) / 2.0)
        c = shapely.centroid(LineString([br, bl]))
        x2, y2 = int(c.x), int(c.y)
        x_new, y_new = x + 2 * (x - x2), y + 2 * (y - y2)
        cv2.circle(frame, (x_new, y_new), 5, (0, 0, 255), 20)
        if id == 47:
            pink.append((x_new, y_new))
        elif id == 13:
            yellow.append((x_new, y_new))
        else:
            brown.append((x_new, y_new))
    return (pink, yellow, brown)


img = cv2.imread("CTS/pics/green_bot.jpeg")
while True:
    try:
        matrix = getWarpMatrix(img)
        break
    except cv2.error:
        print("no aruco")
        pass
img = cv2.warpPerspective(img, matrix, (WIDTH, HEIGHT))
getPucks(img)
# print(cv2.perspectiveTransform(np.float32([grid]), matrix)) # tranforms grid to new grid
cv2.imwrite("CTS/pics/" + "warped.jpeg", img)

# TODO chop off not on board sections of image after tracking aruco
