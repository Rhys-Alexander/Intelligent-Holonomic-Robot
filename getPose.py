import cv2
import numpy as np

points_3D = np.array(
    [
        (-125, 125, 0),  # Nose tip
        (125, 125, 0),  # Chin
        (125, -125, 0),  # Left eye corner
        (-125, -125, 0),  # Right eye corner
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
        for markerCorner in corners:
            success, rvec, tvec = cv2.solvePnP(
                points_3D, markerCorner, cameraMatrix, distCoeffs
            )
            cv2.drawFrameAxes(frame, cameraMatrix, distCoeffs, rvec, tvec, 1000)
    return frame


img = cv2.imread("warped.png")
img = pose(img)
cv2.imwrite("warped.png", img)
