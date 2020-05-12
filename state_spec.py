from legorizer import *
import numpy as np
import os
import psutil
process = psutil.Process(os.getpid())

brickList = GetBrickList()

sil = np.zeros((5,5,5),dtype=bool)
sil[0,:,:] = True
sil[1,0:2,:] = True

state = State(sil, brickList)

b11 = Brick(1,1)
b22 = Brick(2,2)
b33 = Brick(3,3)

state._SetNode(0,0,0, b11)
assert state.IsNewBrickValid(1,0, b11)
assert state.IsNewBrickValid(0,0, b11) == False
assert state.IsNewBrickValid(1.5,1.5,b22)
assert state.IsNewBrickValid(1,1,b22) == False

assert state.IsNewBrickValid(0,0,b33) == False
assert state.IsNewBrickValid(0,3,b33) == False
assert state.IsNewBrickValid(3,0,b33) == False
assert state.IsNewBrickValid(4,4,b33) == False
assert state.IsNewBrickValid(4,2,b33) == False
assert state.IsNewBrickValid(2,4,b33) == False
assert state.IsNewBrickValid(2,2,b33)

state._MoveNextLayer()
assert state.IsNewBrickValid(1,0, b11)
assert state.IsNewBrickValid(2,2, b11) == False
assert state.IsNewBrickValid(0.5,0.5, b22)
assert state.IsNewBrickValid(1.5,1.5, b22) == False
assert state.IsNewBrickValid(-0.5,-0.5, b22) == False

### when addNode still check valid
# sil[:,:,:] = False
# sil[0,0:2,:] = True
# sil[1,:,:] = False
# sil[1,2,2] = True
# state = State(sil)


# for i in range(5):
#     for j in range(5):
#         if (j < 2):
#             assert state.AddBrick(i,j, b11), "i = {}, j = {}".format(i,j)
#         else:
#             assert state.AddBrick(i,j, b11) == False, "i = {}, j = {}".format(i,j)
#             break
# assert state.currentZ == 1
state = State(sil, brickList)
state.AddBrick(1,1,b11)

state2 = state.copy()

assert state == state2

state.AddBrick(2,2,b11)

assert state != state2

sil = np.zeros((5,5,5),dtype=bool)
sil[0,1:4,1:4] = True
sil[0,2:3,0] = True
sil[1,0,0] = True


state = State(sil, brickList)
assert state.topZ == 1, 'state topZ = {} instead of 1'.format(state.topZ) 

for s in state.GetNextStates():
    print(s.nodes)
    print(s.currentLayerSil)

state = State(sil, brickList)

print( 'memory use {} bytes'.format(process.memory_info().rss) )  # in bytes 
