import socket

import pathfinder
import visualiser
import detection as dt

import cv2

BOT_RADIUS = 200
HOST = "10.42.0.1"
PORT = 5005
ADDR = (HOST, PORT)
WIDTH_HEIGHT = (2000, 3000)
OFFSET = (570, 575)
PUCK_RADIUS = 60
BOT_RADIUS = 155

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if ret:
        dtr = dt.Detector(
            img=frame,
            width_height=WIDTH_HEIGHT,
            offset=OFFSET,
            z_height=90,
            goal_height=10,
        )
        if dtr.matrix is not None:
            break

pf = pathfinder.PathFinder(BOT_RADIUS)
vis = visualiser.View(PUCK_RADIUS, BOT_RADIUS)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    bot, pucks, enemies, warped = dtr.get_items(frame)
    cmd, path, graph, nodes = pf.update(pucks, bot, enemies)
    data = cmd.encode()
    client.sendto(data, ADDR)
    img = vis.update(bot, enemies, pucks, path, graph, nodes, warped, cmd)
    cv2.imshow("warped", img)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
