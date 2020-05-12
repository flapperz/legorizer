import numpy as np
from enum import Enum
from queue import PriorityQueue
from heapq import heappush, heappop
from copy import deepcopy
import os
import psutil
import timeit

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

class Brick():
    def __init__(self,w,h):
        self.w = w
        self.h = h
        self.area = w*h

    def __str__(self):
        return "wide = {}, height = {}, area = {}".format(self.w, self.h, self.area)

    def __repr__(self):
        return "Brick {}x{}".format(self.w, self.h)
    
    def __eq__(self, other):
        return self.w == other.w and self.h == other.h

class State():

    def __init__(self, sil, brickList, isCopy=False):
        self.nodes = dict()
        self.redEdges = dict()
        self.blueEdges = dict()
        self.sil = sil
        self.brickList = brickList

        self.currentZ = 0
        self.currentLayerSil = np.zeros(sil[0].shape, dtype=bool)

        if not isCopy:
            dimz, _, _ = sil.shape
            for k in range(dimz-1,-1,-1):
                if np.sum( sil[k] ) != 0:    
                    self.topZ = k
                    break

    def copy(self):
        s = State(self.sil, self.brickList, isCopy=True)
        s.nodes = deepcopy(self.nodes)
        s.redEdge = deepcopy(self.redEdges)
        s.blueEdges = deepcopy(self.blueEdges)

        s.currentZ = self.currentZ
        s.currentLayerSil = np.array(self.currentLayerSil)
        s.topZ = self.topZ
        return s

    def __eq__(self, other):

        if type(self) != type(other):
            return False

        mynodes = self.nodes
        onodes = other.nodes

        if set(mynodes.keys()) != set(onodes.keys()):
            return False
            
        for k in mynodes:
            if set(mynodes[k].keys()) != set(onodes[k].keys()):
                return False
            
        for k in mynodes:
            for j in mynodes[k]:
                if set(mynodes[k][j].keys()) != set(onodes[k][j].keys()):
                    return False
        
        return True
    
    def __

    def IsFinish(self):
        return self.currentZ == self.topZ+1

    def GetNextStates(self):
        '''O ( dimx * dimy * No brick * O( Add ) )'''
        z = self.currentZ
        dimy, dimx = self.currentLayerSil.shape
        nextStates = []

        for j in range(dimy):
            for i in range(dimx):
                for brick in self.brickList:

                    if not self.sil[z][j][i]:
                        continue
                    if self.currentLayerSil[j][i]:
                        continue

                    if self.IsNewBrickValid(i,j,brick):
                        newState = self.copy()
                        newState.AddBrick(i,j, brick)

                        nextStates.append(newState)
                        break

        return nextStates

    def CalHeuristic(self):
        return random() #TODO

    def _MoveNextLayer(self):
        self.currentLayerSil = np.zeros(self.sil[0].shape, dtype=bool)
        self.currentZ += 1

    def _SetNode(self, x, y, z, brick):

        if z not in self.nodes:
            self.nodes[z] = dict()

        if y not in self.nodes[z]:
            self.nodes[z][y] = dict()

        self.nodes[z][y][x] = brick

        beginx  =   int( x - brick.w/2 + 0.5 )
        endx    =   int( x + brick.w/2 + 0.5 )
        beginy  =   int( y - brick.h/2 + 0.5 )
        endy    =   int( y + brick.h/2 + 0.5 )

        self.currentLayerSil[beginy:endy,beginx:endx] = True

    def IsNewBrickValid(self, x, y, newbrick):

        z = self.currentZ
        dimy,dimx = self.currentLayerSil.shape

        beginx  =   int( x - newbrick.w/2 + 0.5 )
        endx    =   int( x + newbrick.w/2 + 0.5 )
        beginy  =   int( y - newbrick.h/2 + 0.5 )
        endy    =   int( y + newbrick.h/2 + 0.5 )

        if beginx < 0 or endx > dimx:
            return False
        if beginy < 0 or endy > dimy:
            return False

        for i in range(beginx, endx):
            for j in range(beginy, endy):
                if not self.sil[z][j][i]:
                    return False
                if self.currentLayerSil[j][i]:
                    return False
        return True

    def IsLayerFull(self):
        return np.sum( np.bitwise_xor(self.currentLayerSil, self.sil[self.currentZ] ) ) == 0

    def AddBrick(self, x, y, brick):
        ''' O( IsNewBrickValid) '''
        z = self.currentZ
        # if not self.IsNewBrickValid(x,y, brick):
        #     return False
        # TODO set red, blue edges
        self._SetNode(x,y,z, brick)

        if self.IsLayerFull():
            self._MoveNextLayer()

        return True

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
        
        states = current.GetNextStates()
        print('consider at layer {}'.format(current.currentZ), current.nodes)

        for state in states:
            if state.IsFinish():
                print('finish ', state.nodes)
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

    # voxs = ReadVoxs( VOX_IN_PATH )
    # sil = voxs != 255
    sil = np.zeros((5,5,5),dtype=bool)
    sil[0,1:4,1:4] = True
    sil[0,2:3,0] = True

    brickList = GetBrickList()

    Solve(sil, brickList)
    # SaveVoxs( VOX_OUT_PATH, voxs, CreatePalette() )

    stop = timeit.default_timer()
    process = psutil.Process(os.getpid())
    print( 'memory use {} bytes'.format(process.memory_info().rss) )  # in bytes 
    print( 'execution time {}'.format(stop-start))