import sys
import pathfinder
import visualiser as vis
import detection as dt
import cv2
import socket

BOT_RADIUS = 200
HOST = "10.42.0.1"
PORT = 5005
ADDR = (HOST, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if ret:
        break
dtr = dt.Detector(frame)
pf = pathfinder.PathFinder()
board = vis.Board()

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    bot, pucks, enemies, warped = dtr.getItems(frame)
    path, graph, nodes = pf.update(pucks, bot, enemies)
    data = path.encode()
    client.sendto(data, ADDR)
    print(data.strip())
    print(pucks)
    img = board.update(bot, enemies, pucks, path, graph, nodes, warped)
    cv2.imshow("warped", img)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
