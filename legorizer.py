import numpy as np
from enum import Enum
from queue import PriorityQueue
from heapq import heappush, heappop
from voxHelpers import *

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

class Brick():
    def __init__(self,w,h):
        self.w = w
        self.h = h
        self.area = w*h
    def __str__(self):
        return "wide = {}, height = {}, area = {}".format(self.w, self.h, self.area)

class State():

    def __init__(self, voxs):
        self.nodes = dict()
        self.redEdges = dict()
        self.blueEdges = dict()
        self.voxs = voxs

        self.tillingLayer = np.ndarray(voxs[0], dtype=object)
        self.tillingLayer = (tillingLayer != Vox.EMPTY).fill 

    def AddNode(self, x, y, z, brick):

        if z not in self.nodes:
            self.nodes[z] = dict()

        if y not in self.nodes[z]:
            self.nodes[z][y] = dict()

        self.nodes[z][y][x] = brick

def GetBrickList():
    # TODO LOAD BRICK
    originalBrickList = [(1,1), (1,2), (1,3), (2,2), (2,4), (2,6), (2,3), (2,8)]
    brickList = [ Brick(x[0],x[1]) for x in originalBrickList ] + [ Brick(x[1],x[0]) for x in originalBrickList ]

    return sorted( brickList, key=lambda b: b.area, reverse=True )

def Solve(voxs, brickList):

    dimz, dimy, dimx = voxs.shape

    OPEN = []
    CLOSED = set()
    
    OPEN.append( (0, 'start node') ) #TODO
    while(True):
        current = heappop(OPEN)

        # states = GetNextStates(current)

        for state in states:
            if not state.valid:
                continue

            if state.finish:
                return state

            if state not in OPEN:
                # G = CalHeuristic(state)
                G = 0
                heappush(OPEN, (G, state) )


        print(current)
        if not len(OPEN):
            break

        


    soln = np.zeros((dimz, dimy, dimx), dtype=int)
    return soln
    

if __name__ == '__main__':

    voxs = ReadVoxs( VOX_IN_PATH )
    brickList = GetBrickList()

    # Solve(voxs, brickList)
    SaveVoxs( VOX_OUT_PATH, voxs, CreatePalette() )