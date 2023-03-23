import sys
import pathfinder
import detection as dt
import cv2


if len(sys.argv) > 1:
    if sys.argv[1] == "green":
        blueTeam = False
    elif sys.argv[1] == "blue":
        blueTeam = True
    else:
        print("Invalid argument, use green or blue")
        exit()
else:
    print("No argument given, defaulting to blue")
    blueTeam = True

# TODO write start Phase
# TODO write main phase
# TODO write steal phase
# TODO write end phase
# TODO estimate score at end

# TODO get image from camera


# Sample Data
BOT_RADIUS = 200
CHERRY_BOT_RADIUS = 160
pucks = (
    [(225, 575), (1775, 575), (225, 2425), (1775, 2425)]
    + [(225, 775), (1775, 775), (225, 2225), (1775, 2225)]
    + [(725, 1125), (1275, 1125), (725, 1875), (1275, 1875)]
)
# tuple, x pos, y pos, rotation
bot = (225, 225, 0) if blueTeam else (1775, 225, 0)
cherry_bot = (
    (225 + BOT_RADIUS + CHERRY_BOT_RADIUS + 30, 225, 0)
    if blueTeam
    else (1775 - BOT_RADIUS - CHERRY_BOT_RADIUS - 30, 225, 0)
)
enemy_bot = (1775, 225, 0) if blueTeam else (225, 225, 0)
enemy_bots = [enemy_bot]
# lists of tuples, x pos, y pos
cherries = [
    (1000, CHERRY_BOT_RADIUS),
    (1000, 3000 - CHERRY_BOT_RADIUS),
    (15, 1500),
    (1985, 1500),
]
MAX_CAPACITY = 18
capacity = MAX_CAPACITY


img = cv2.imread("CTS/input_pics/multi_bots.jpeg")
dtr = dt.Detector(blueTeam=True, img=img)
pf = pathfinder.PathFinder(blueTeam)
# while True:
img = cv2.imread("CTS/input_pics/multi_bots.jpeg")
# bots, pucks, img = dtr.getItems(img)
# bot = bots[0]
# cherry_bot = bots[1]
# enemy_bots = bots[2:]
pf.update(pucks, bot, cherry_bot, enemy_bots, cherries, capacity)
pf.displayGraph()
