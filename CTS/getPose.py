import cv2
import numpy as np
from shapely.geometry import Point, LineString
from shapely import centroid, coords

points_3D = np.array(
    [
        (-125, 125, 0),
        (125, 125, 0),
        (125, -125, 0),
        (-125, -125, 0),
    ],
    dtype="double",
)

distCoeffs = np.zeros((4, 1))


def pose(frame):
    size = frame.shape
    cameraMatrix = np.array(
        [
            [size[1], 0, size[1] / 2],
            [0, size[1], size[0] / 2],
            [0, 0, 1],
        ]
    )
    # get grid
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, params)
    corners, ids, _ = detector.detectMarkers(frame)
    if len(corners) > 0:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        for markerCorner, id in zip(corners, ids):
            if id in [47, 13, 36]:
                success, rvec, tvec = cv2.solvePnP(
                    points_3D, markerCorner, cameraMatrix, distCoeffs
                )
                tl, tr, br, bl = markerCorner.reshape((4, 2))
                x = int((tl[0] + br[0]) / 2.0)
                y = int((tl[1] + br[1]) / 2.0)
                c = centroid(LineString([br, bl]))
                x2, y2 = int(c.x), int(c.y)
                x_new, y_new = x + 2 * (x - x2), y + 2 * (y - y2)

                cv2.drawFrameAxes(frame, cameraMatrix, distCoeffs, rvec, tvec, 1000)
                cv2.circle(frame, (int(x_new), int(y_new)), 5, (0, 0, 255), 20)

    return frame


img = cv2.imread("CTS/pics/warped.jpeg")
img = pose(img)
cv2.imwrite("CTS/pics/warped.jpeg", img)
