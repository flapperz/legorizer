from _state import *

b1x1 = Brick(1, 1)
b2x2 = Brick(2, 2)
b3x3 = Brick(3, 3)

b3x1 = Brick(3, 1)
b1x2 = Brick(1, 2)


# Check brick touch for blue edge
assert CheckBrickTouch(b2x2, 0.5, 0.5, b2x2, 2.5, 0.5)
assert CheckBrickTouch(b2x2, 0.5, 0.5, b2x2, 0.5, 2.5)
assert CheckBrickTouch(b2x2, 0.5, 0.5, b2x2, 2.5, 2.5) == False
assert CheckBrickTouch(b2x2, 0.5, 0.5, b2x2, 3, 3) == False

assert CheckBrickTouch(b3x3, 1, 1, b3x3, 4, 2)
assert CheckBrickTouch(b3x3, 1, 1, b3x3, 3, 4)
assert CheckBrickTouch(b3x3, 1, 1, b3x3, 4, 4) == False
assert CheckBrickTouch(b3x3, 1, 1, b2x2, 4.5, 3) == False

assert CheckBrickTouch(b1x2, 1, 1.5, b3x1, 1, 0)

# Check brick connect
assert CheckBrickConnect(b3x3, 1, 1, b2x2, -0.5, -0.5)
assert CheckBrickConnect(b3x3, 1, 1, b2x2, -0.5, 1.5)
assert CheckBrickConnect(b3x3, 1, 1, b2x2, 2.5, 0.5)
assert CheckBrickConnect(b3x3, 1, 1, b2x2, 2.5, 2.5)
assert CheckBrickConnect(b3x3, 1, 1, b1x1, 1, 1)

assert CheckBrickConnect(b3x3, 1, 1, b1x1, -1, 1) == False
assert CheckBrickConnect(b3x3, 1, 1, b1x1, 3, 1) == False
assert CheckBrickConnect(b3x3, 1, 1, b1x1, 1, 3) == False
assert CheckBrickConnect(b3x3, 1, 1, b1x1, 3, 3) == False


