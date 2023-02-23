import cv2
import numpy as np

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


def getObjectCoods(hsv, frame, hsvColor):
    hsvVal, bgr, prec, kernelSize, sortFunc = hsvColor
    coods = []
    hsvVal = [int(hsvVal[0] / 2)] + [int(v / 100 * 255) for v in hsvVal[1:]]
    low = np.array([v - prec if v > prec else 0 for v in hsvVal])
    upp = np.array([v + prec if v < 255 - prec else 255 for v in hsvVal])
    mask = cv2.inRange(hsv, low, upp)
    kernel = np.ones(kernelSize, np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    for i in sortFunc(contours):
        M = cv2.moments(i)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            coods.append((cx, cy))
            cv2.drawContours(frame, [i], -1, bgr, 4)
    return coods


def draw(frame, gray=False):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if gray:
        frame = cv2.cvtColor(
            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR
        )
    for color in HSVCOLORS:
        for p in getObjectCoods(hsv, frame, color):
            cv2.circle(frame, p, 10, color[1], -1)
    return frame


def warp(frame):
    # get grid
    grid = [0] * 4
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, params)
    corners, ids, _ = detector.detectMarkers(frame)
    if len(corners) > 0:
        ids = ids.flatten()
        for (markerCorner, markerID) in zip(corners, ids):
            tl, _, br, _ = markerCorner.reshape((4, 2))
            cX = int((tl[0] + br[0]) / 2.0)
            cY = int((tl[1] + br[1]) / 2.0)
            if markerID in [20, 21, 22, 23]:
                grid[markerID % 20] = (cX, cY)
    # warp based on grid
    bWidth, bHeight = 2000, 3000
    bw_seg, bh_seg = bWidth / 7, bHeight / 5
    width, height = int(bWidth * 1.2), int(bHeight * 1.2)
    w_seg, h_seg = width / 12, height / 12
    # width, height = bWidth, bHeight
    # w_seg, h_seg = 0, 0
    pts1 = np.float32(grid)
    pts2 = np.float32(
        [
            [w_seg + bw_seg * 2, h_seg + bh_seg],
            [w_seg + bWidth - bw_seg * 2, h_seg + bh_seg],
            [w_seg + bw_seg * 2, h_seg + bh_seg * 4],
            [w_seg + bWidth - bw_seg * 2, h_seg + bh_seg * 4],
        ]
    )
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    # print(cv2.perspectiveTransform(np.float32([grid]), matrix)) # tranforms grid to new grid
    return cv2.warpPerspective(frame, matrix, (width, height))


img = cv2.imread("example.jpeg")
# img = draw(img, True)
img = warp(img)
cv2.imwrite("warped.png", img)

# TODO chop off not on board sections of image after tracking aruco
