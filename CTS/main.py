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


# Sample Data
BOT_RADIUS = 200
CHERRY_BOT_RADIUS = 160
# pucks = (
#     [(225, 575), (1775, 575), (225, 2425), (1775, 2425)]
#     + [(225, 775), (1775, 775), (225, 2225), (1775, 2225)]
#     + [(725, 1125), (1275, 1125), (725, 1875), (1275, 1875)]
# )
# # tuple, x pos, y pos, rotation
# bot = (225, 225, 0) if blueTeam else (1775, 225, 0)
# cherry_bot = (
#     (225 + BOT_RADIUS + CHERRY_BOT_RADIUS + 30, 225, 0)
#     if blueTeam
#     else (1775 - BOT_RADIUS - CHERRY_BOT_RADIUS - 30, 225, 0)
# )
# enemy_bot = (1775, 225, 0) if blueTeam else (225, 225, 0)
# enemy_bots = [enemy_bot]
# # lists of tuples, x pos, y pos
cherries = [
    (1000, CHERRY_BOT_RADIUS),
    (1000, 3000 - CHERRY_BOT_RADIUS),
    (15, 1500),
    (1985, 1500),
]
MAX_CAPACITY = 18
capacity = MAX_CAPACITY


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
    bot = bots[0]
    cherry_bot = (0, 0, 0)
    enemy_bots = []
    data = pf.update(pucks, bot, enemy_bots, capacity)
    print(data.strip())
    print(pucks)
    data = data.encode()
    client.sendto(data, ADDR)
    if data == "!EXIT":
        print("Disconneted from the server.")
        break
    data, addr = client.recvfrom(1024)
    data = data.decode()
    print(f"Server: {data}")

cap.release()
