import sys
import pathfinder
import detection as dt
import cv2
import socket

HOST = "10.42.0.1"
PORT = 5005
ADDR = (HOST, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# TODO write start Phase
# TODO write main phase
# TODO write steal phase
# TODO write end phase
# TODO estimate score at end

# TODO get image from camera


BOT_RADIUS = 200

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if ret:
        img = frame
        break
dtr = dt.Detector(blueTeam=True, img=img)
pf = pathfinder.PathFinder()
while True:
    ret, img = cap.read()
    if not ret:
        continue
    bots, pucks, img = dtr.getItems(img)
    cv2.imshow("board", img)
    if cv2.waitKey(1) == ord("q"):
        break
    bot = bots[0]
    cherry_bot = (0, 0, 0)
    enemy_bots = []
    data = pf.update(pucks, bot, enemy_bots, capacity)
    print(data.strip())
    print(pucks)
    data = data.encode()
    client.sendto(data, ADDR)

cap.release()
cv2.destroyAllWindows()
