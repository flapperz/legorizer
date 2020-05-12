from enum import Enum
from heapq import heappush, heappop
from copy import deepcopy
import os
import psutil
import timeit
from _brick import *
from _state import *

from voxHelpers import *

from random import random
import logging


# constants && enums
VOX_IN_PATH = './voxin/out.slab.vox'
VOX_OUT_PATH = './legorized.vox'
    

class Vox():
    VOXSURF_EMPTY = 255
    VOXSURF_SHELL = 127
    VOXSURF_INSIDE = 123

    EMPTY = 255
    SHELL = 127
    INSIDE = 123

def GetBrickList():
    # TODO LOAD BRICK
    originalBrickList = [(1,1), (1,2), (1,3), (2,2), (2,4), (2,6), (2,3), (2,8)]
    brickList = [ Brick(x[0],x[1]) for x in originalBrickList ] + [ Brick(x[1],x[0]) for x in originalBrickList ]

    return sorted( brickList, key=lambda b: b.area, reverse=True )

def Solve(sil, brickList):

    dimz, dimy, dimx = sil.shape

    OPEN = []
    CLOSED = set()
    
    OPEN.append( (0, State(sil, brickList)) )
    while(True):
        current = heappop(OPEN)[1]

        # maintain uniqueness at level 1 only
        if (current.currentZ == 0):
            CLOSED.add(current)

        states = current.GetNextStates()
        # print('consider at layer {}'.format(current.currentZ), current)
        print('layer: {}, size heap: {}'.format(current.currentZ, len(OPEN)))
        for state in states:
            if current.currentZ == 0 and state in CLOSED:
                continue

            if state.IsFinish():
                print('finish ', state)
                return state
            if state not in OPEN:
                G = state.CalHeuristic()
                heappush(OPEN, (G, state) )

        if not len(OPEN):
            break

    soln = np.zeros((dimz, dimy, dimx), dtype=int)
    return soln

    

if __name__ == '__main__':

    start = timeit.default_timer()

    voxs = ReadVoxs( VOX_IN_PATH )
    sil = voxs != 255
    # sil = np.zeros((5,5,5),dtype=bool)
    # sil[0,1:4,1:4] = True
    # sil[0,2:3,0] = True

    brickList = GetBrickList()

    finstate = Solve(sil, brickList)
    # SaveVoxs( VOX_OUT_PATH, voxs, CreatePalette() )

    stop = timeit.default_timer()
    process = psutil.Process(os.getpid())
    print( 'memory use {} bytes'.format(process.memory_info().rss) )  # in bytes 
    print( 'execution time {}'.format(stop-start))