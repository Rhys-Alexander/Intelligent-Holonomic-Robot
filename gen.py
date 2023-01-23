import cv2


dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
x = cv2.aruco.generateImageMarker(dictionary, 0, 200)
y = cv2.imwrite("marker.png", x)
