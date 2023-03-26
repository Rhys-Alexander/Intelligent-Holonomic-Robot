# cakes
POINT_PER_LAYER = 1
LEGEND_POINTS = 4
# Cake Cherries
POINTS_PER_CHERRY_CAKE = 3
# Dropping Cherries
POINTS_FOR_BASKET = 5
POINTS_FOR_CORRECT_COUNT = 5
# end on platter
POINTS_FOR_ENDING_ON_PLATTER = 15
# Disguise
POINTS_FOR_DISGUISE = 5

LEGEND = ["Icing", "Cream", "Sponge Cake"]

# TODO get number of cakes that are in plate and account for a maximum of 3 cakes
# TODO on each of those cakes check if there is red on the cake to get cherries
# TODO connect to basket arduino to get the number of cherries in the basket


def getPoints(cakes, cherries, basketCherries):
    points = POINTS_FOR_BASKET
    for cake in cakes:
        if cake == LEGEND:
            points += LEGEND_POINTS
        points += POINT_PER_LAYER * len(cake)
    points += POINTS_PER_CHERRY_CAKE * len(cherries)
    points += basketCherries + POINTS_FOR_CORRECT_COUNT


def getEndPoints(cakes, cherries, basketCherries):
    points = getPoints(cakes, cherries, basketCherries)
    points += POINTS_FOR_ENDING_ON_PLATTER + POINTS_FOR_DISGUISE
