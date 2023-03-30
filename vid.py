import cv2

cap = cv2.VideoCapture(0)
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, params)

while True:
    ret, frame = cap.read()
    if ret is False:
        continue
    corners, ids, rejected = detector.detectMarkers(frame)
    if len(corners) > 0:
        ids = ids.flatten()
        for (corner, id) in zip(corners, ids):
            corners = corner.reshape((4, 2))
            (tl, tr, br, bl) = corners
            tr = (int(tr[0]), int(tr[1]))
            br = (int(br[0]), int(br[1]))
            bl = (int(bl[0]), int(bl[1]))
            tl = (int(tl[0]), int(tl[1]))

            cv2.line(frame, tl, tr, (0, 255, 0), 2)
            cv2.line(frame, tr, br, (0, 255, 0), 2)
            cv2.line(frame, br, bl, (0, 255, 0), 2)
            cv2.line(frame, bl, tl, (0, 255, 0), 2)
            cX = int((tl[0] + br[0]) / 2.0)
            cY = int((tl[1] + br[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)
            cv2.putText(
                frame,
                str(id),
                (tl[0], tl[1] - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                10,
                (0, 255, 0),
                10,
            )

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
