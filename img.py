import cv2
import numpy as np


img = cv2.imread("board2.png")

HSVCOLORS = (
    # ((H, S, V), (B, G, R))
    ((15, 53, 24), (0, 100, 255)),  # brown
    ((333, 60, 60), (230, 0, 255)),  # pink
    ((40, 80, 80), (0, 255, 255)),  # yellow
)


def drawSliceMask(hsvVal, bgr, hsv, frame):
    prec = 45
    hsvVal = [int(hsvVal[0] / 2)] + [int(v / 100 * 255) for v in hsvVal[1:]]
    low = np.array([v - prec if v > prec else 0 for v in hsvVal])
    upp = np.array([v + prec if v < 255 - prec else 255 for v in hsvVal])
    mask = cv2.inRange(hsv, low, upp)
    kernel = np.ones((20, 20), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    for i in sorted(contours, key=cv2.contourArea, reverse=True)[:4]:
        M = cv2.moments(i)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.drawContours(frame, [i], -1, bgr, 4)
            cv2.circle(frame, (cx, cy), 4, bgr, -1)


def drawCherries(hsv, frame):
    hsvVal, bgr = (6, 76, 71), (0, 0, 255)
    prec = 25
    hsvVal = [int(hsvVal[0] / 2)] + [int(v / 100 * 255) for v in hsvVal[1:]]
    low = np.array([v - prec if v > prec else 0 for v in hsvVal])
    upp = np.array([v + prec if v < 255 - prec else 255 for v in hsvVal])
    mask = cv2.inRange(hsv, low, upp)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    for i in filter(lambda x: cv2.contourArea(x) < 1000, contours):
        M = cv2.moments(i)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.drawContours(frame, [i], -1, bgr, 4)
            cv2.circle(frame, (cx, cy), 3, bgr, -1)


def draw(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = frame
    # gray = cv2.cvtColor(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    for color in HSVCOLORS:
        drawSliceMask(color[0], color[1], hsv, gray)
    drawCherries(hsv, gray)
    return gray


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
            grid[markerID % 20] = (cX, cY)
    # warp based on grid
    bWidth, bHeight = 2000, 3000
    width, height = int(bWidth * 1.2), int(bHeight * 1.2)
    bw_seg, bh_seg = bWidth / 7, bHeight / 5
    w_seg, h_seg = width / 12, height / 12
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
    return cv2.warpPerspective(frame, matrix, (width, height))


# img = warp(img)

cv2.imshow("IMG", draw(img))
cv2.waitKey(0)
cv2.destroyAllWindows()
